#!/usr/bin/env python3
"""fill-template.py -- Fill {{Token}} placeholders in Word/PowerPoint/Excel templates.

Positional CLI (Agent Skills compatible):

    python3 fill-template.py <template.(docx|pptx|xlsx)> <data.json> <output> [--audit]

How it works
    - data.json is a flat object mapping token name -> single-line string value.
    - Tokens look like {{ClientName}} or {{client_name}}; names may contain
      letters, digits, spaces, dots, hyphens and underscores.
    - Values must not contain further {{...}} tokens. Empty string "" is valid.
    - Missing keys are left intact in the output and reported on stderr;
      the script still writes its output, then exits 3 so callers can retry.
    - Placeholders split across several XML text runs (common when users edit
      Word in the middle of a token) are re-merged automatically.

Why stdlib only
    zipfile + re only -- no network, no package installs. The script therefore
    runs unchanged inside the Microsoft Copilot skill sandbox and locally
    (on Windows use: py -3 fill-template.py ...).

Covered parts (per file type)
    .docx  word/document.xml, word/header*.xml, word/footer*.xml,
           word/footnotes.xml, word/endnotes.xml                        tag: w:t
    .pptx  ppt/slides/*.xml, slideLayouts, slideMasters,
           notesSlides, notesMasters                                    tag: a:t
    .xlsx  xl/sharedStrings.xml and inline strings in
           xl/worksheets/sheetS.xml                                     tag: t

Limitations (documented, deliberate v1 scope)
    - Numbers are written as text cells; template formatting must expect that.
    - Chart labels and debug-visible parts (e.g. w:instrText) are not scanned.
    - Values are single-line; newline characters become spaces.

Exit codes: 0 ok | 1 usage | 2 file/zip error | 3 missing or unbalanced tokens
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

EXIT_OK, EXIT_USAGE, EXIT_FILE, EXIT_MISSING = 0, 1, 2, 3

# A token: {{  optional space  name  optional space  }}
# The name is captured lazily so a trailing space belongs to the closer.
TOKEN_RE = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_. \-]{0,62}?)\s*\}\}")

DOCX_PARTS = re.compile(r"^word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$")
PPTX_PARTS = re.compile(
    r"^ppt/(slides|slideLayouts|slideMasters|notesSlides|notesMasters)/[^/]+\.xml$"
)
XLSX_PARTS = re.compile(r"^(xl/sharedStrings\.xml|xl/worksheets/sheet\d+\.xml)$")

RULES = {
    ".docx": (DOCX_PARTS, "w:t"),
    ".pptx": (PPTX_PARTS, "a:t"),
    ".xlsx": (XLSX_PARTS, "t"),
}


def span_re(tag: str) -> "re.Pattern[str]":
    """Regex matching every text node of a given tag together with its body."""
    return re.compile(r"<%s(?:\s[^>]*)?>([^<]*)</%s>" % (tag, tag))


def tokenize_body(body: str, report: "set[str]") -> str:
    """Append every token name found in body to report (no substitution)."""
    report.update(name.strip() for name in TOKEN_RE.findall(body))
    return body


def fill_bodies(xml: str, sre: "re.Pattern[str]", data: dict, filled: list, missing: set) -> str:
    """Replace complete tokens inside single text nodes; keep missing ones."""

    def _sub_span(m: "re.Match[str]") -> str:
        body = m.group(1)

        def _sub_token(tm: "re.Match[str]") -> str:
            name = tm.group(1).strip()
            value = data.get(name)
            if name in data and value is not None:
                filled.append(name)
                return escape(str(value))
            missing.add(name)
            return tm.group(0)

        new_body = TOKEN_RE.sub(_sub_token, body)
        if new_body == body:
            return m.group(0)
        return m.group(0)[: m.start(1) - m.start(0)] + new_body + m.group(0)[m.end(1) - m.start(0):]

    return sre.sub(_sub_span, xml)


def merge_pass(xml: str, sre: "re.Pattern[str]") -> tuple[str, bool]:
    """Pull following text nodes' content into any node carrying an open '{{'.

    Tokens split across runs (or across <w:r>/<w:t> boundaries) end up fully in
    the first node; the following nodes are emptied. Markup between nodes is
    preserved (an empty <w:t/> is legal), so document structure never changes.
    Merges repeat until no text node is left with an unbalanced '{{' or the
    node has no following node that can close it (cross-parts never merge).
    """
    changed = False
    merges = 0
    max_merges = 2000  # runaway guard for unclosed tokens at part end
    while merges < max_merges:
        spans = list(sre.finditer(xml))
        target = next(
            (i for i, s in enumerate(spans) if s.group(1).count("{{") > s.group(1).count("}}")),
            None,
        )
        if target is None:
            break
        j = next(
            (i for i in range(target + 1, len(spans)) if spans[i].group(1)),
            None,
        )
        if j is None:
            break  # no following node can close this token (e.g. cross-part)
        first, second = spans[target], spans[j]
        merged_body = first.group(1) + second.group(1)
        # Empty the later node first (its offsets are unaffected when the
        # earlier node then grows).
        xml = xml[: second.start(1)] + xml[second.end(1):]
        xml = xml[: first.start(1)] + merged_body + xml[first.end(1):]
        changed = True
        merges += 1
    return xml, changed


def split_run_totals(xml: str, sre: "re.Pattern[str]") -> dict:
    """Diagnostics: token counts over concatenated text, unbalanced opens."""
    bodies = [m.group(1) for m in sre.finditer(xml)]
    text = "".join(bodies)
    opened = "{{" if text.count("{{") > text.count("}}") else None
    return {"opens": text.count("{{"), "closes": text.count("}}"), "unbalanced": opened}


def fill_part(xml: str, tag: str, data: dict, filled: list) -> tuple[str, set, int, int]:
    """Fill a single part file; returns (new_xml, missing, merges, rounds)."""
    sre = span_re(tag)
    missing: set[str] = set()
    merges = rounds = 0
    for _ in range(5):  # bounded convergence
        rounds += 1
        before = xml
        xml = fill_bodies(xml, sre, data, filled, missing)
        xml, changed = merge_pass(xml, sre)
        xml = fill_bodies(xml, sre, data, filled, missing)
        if changed:
            merges += 1
        if xml == before and not changed:
            break
    return xml, missing, merges, rounds


def load_data(path: Path) -> tuple[dict, list]:
    """Load flat token/value map; returns (data, warnings) with only str values kept."""
    with path.open("r", encoding="utf-8-sig") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        raise ValueError("data.json must be a JSON object mapping token name to value")
    data, dropped = {}, []
    for key, value in raw.items():
        if isinstance(value, str):
            data[key.strip()] = value.replace("\r\n", " ").replace("\n", " ")
        else:
            dropped.append(key)
    warnings = ["dropped non-string value for token %r (v1 supports strings only)" % k for k in dropped]
    return data, warnings


def process(template: Path, data_path: Path, output: Path, audit: bool):
    ext = template.suffix.lower()
    if ext not in RULES:
        raise ValueError("unsupported template type %r (expected .docx, .pptx or .xlsx)" % ext)
    part_filter, tag = RULES[ext]
    sre = span_re(tag)

    data, warnings = load_data(data_path)

    seen_tokens: set[str] = set()
    filled: list[str] = []
    parts_touched: list[str] = []
    out_buf = {}

    with zipfile.ZipFile(template, "r") as zin:
        infos = zin.infolist()  # keep original entry order
        for info in infos:
            blob = zin.read(info.filename)
            if part_filter.match(info.filename):
                xml = blob.decode("utf-8")
                for m in sre.finditer(xml):
                    tokenize_body(m.group(1), seen_tokens)
            out_buf[info.filename] = (info, blob)

    # Full pass over matching parts (live fill)
    missing: set[str] = set()
    for name, (info, blob) in list(out_buf.items()):
        if part_filter.match(name):
            xml = blob.decode("utf-8")
            new_xml, part_missing, merges, rounds = fill_part(xml, tag, data, filled)
            missing.update(part_missing)
            out_buf[name] = (info, new_xml.encode("utf-8"))
            parts_touched.append(name)

    # Post-fill truth: what remains in the output ARE the missing tokens;
    # unused keys are those never present in the template (merged or single).
    left_in_output = sorted(
        {tok.strip() for name, (_info, blob) in out_buf.items()
         if part_filter.match(name)
         for mm in span_re(tag).finditer(blob.decode("utf-8"))
         for tok in TOKEN_RE.findall(mm.group(1))}
    )
    filled_names = sorted(set(filled))
    missing_names = list(left_in_output)
    unused_names = sorted(k for k in data if k not in seen_tokens and k not in filled_names)
    unbalanced = [
        name for name, (_info, blob) in out_buf.items()
        if part_filter.match(name)
        and split_run_totals(blob.decode("utf-8"), span_re(tag))["unbalanced"]
    ]

    report = {
        "template": template.name,
        "tags": tag,
        "parts_filled": parts_touched,
        "filled_count": len(filled),
        "filled_names": filled_names,
        "missing_in_data": missing_names,
        "unused_data_keys": unused_names,
        "left_in_output": left_in_output,
        "unbalanced_parts": unbalanced,
        "warnings": warnings,
    }

    print(json.dumps(report, indent=2))
    if missing_names or unused_names:
        print(
            "ERROR: missing tokens: %s | unknown data keys: %s"
            % (missing_names or "none", unused_names or "none"),
            file=sys.stderr,
        )

    if audit:
        return EXIT_MISSING if (missing_names or unbalanced) else EXIT_OK

    # Re-zip: identical entries/order/compression/dates; only text parts changed.
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, blob in out_buf.values():
            zinfo = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zinfo.compress_type = info.compress_type
            zinfo.external_attr = info.external_attr
            zout.writestr(zinfo, blob)

    if missing_names:
        print("Output written with %d unresolved token(s) left intact." % len(missing_names),
              file=sys.stderr)
        return EXIT_MISSING
    return EXIT_OK


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--audit"]
    audit = "--audit" in argv[1:]
    if len(args) != 3:
        print(__doc__)
        return EXIT_USAGE
    template, data_path, output = (Path(a) for a in args)
    try:
        return process(template, data_path, output, audit)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return EXIT_FILE


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
