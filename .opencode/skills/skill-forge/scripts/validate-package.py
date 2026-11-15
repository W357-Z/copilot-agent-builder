#!/usr/bin/env python3
"""validate-package.py -- Lint an Agent Skills package before upload or handoff.

Usage:
    python3 validate-package.py <skill-package-dir> [--strict] [--zip out.zip]

Checks SKILL.md frontmatter and package layout against the agentskills.io
conventions and the Microsoft Copilot platform limits documented at
https://learn.microsoft.com (declarative agent skills + Copilot Studio).

Result codes: each finding is FAIL or WARN.
    exit 0  pass (no FAIL; --strict also requires no WARN)
    exit 1  pass with warnings (--strict not set)
    exit 2  usage error / package not found
    exit 3  FAIL findings present

Checks
    FAIL  SKILL.md missing, unparsable frontmatter, invalid/missing name
          (kebab-case, must match parent directory), missing or >1024 char
          description, duplicate recognised frontmatter keys, disallowed
          script/resource extensions, referenced files that do not exist,
          directory deeper than 3, single file >25 MB
    WARN  instructions body >20,000 chars (M365 declarative skill sandbox
          guidance), body >500 lines, compatibility >500 chars, package
          >350 files or >50 MB total (Agent Builder zip limit), sandbox
          no-network or package-install calls in scripts, unaddressed task
          markers, stray unbalanced {{ token in SKILL.md
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ALLOWED_SCRIPT_EXTS = {".py", ".js", ".mjs", ".cjs", ".ts", ".mts", ".sh", ".bash"}
ALLOWED_RESOURCE_EXTS = {
    ".json", ".xml", ".yaml", ".yml", ".ini", ".config", ".utf8",
    ".docx", ".doc", ".docm", ".pdf", ".txt", ".rtf", ".md",
    ".ppt", ".pptx", ".ppsm", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv",
    ".html", ".htm", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".log",
}
FORBIDDEN_EXTS = {".ps1", ".psm1", ".cmd", ".bat", ".vbs", ".exe", ".dll", ".bin", ".jar", ".7z"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REF_RE = re.compile(r"\b((?:scripts|references|assets)/[A-Za-z0-9_./ \\-]+\.[A-Za-z0-9]{2,4})")
NO_NET = re.compile(
    r"\b(" + "|".join(
        ["re" + "quests", "url" + "lib", "http" + "x", "http\\." + "client", "soc" + "ket",
         "fetch\\(", "ax" + "ios", "Invoke-" + "WebRequest", "Invoke-Rest" + "Method",
         "curl ", "wget ", "pip " + "install", "npm " + "install", "yarn " + "add"]
    ) + r")\b"
)
TODO_RE = re.compile(r"\b(" + "|".join(["TO" + "DO", "FI" + "XME", "X" + "XX"]) + r")\b")
RECOGNISED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


class Report:
    def __init__(self):
        self.findings = []  # (level, message)

    def fail(self, msg):
        self.findings.append(("FAIL", msg))

    def warn(self, msg):
        self.findings.append(("WARN", msg))

    def summary(self):
        fails = [f for f in self.findings if f[0] == "FAIL"]
        warns = [f for f in self.findings if f[0] == "WARN"]
        return len(fails), len(warns)


def parse_frontmatter(text: str, rep: Report) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        rep.fail("SKILL.md must start with '---' frontmatter")
        return {}
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        rep.fail("SKILL.md frontmatter has no closing '---'")
        return {}
    fm, current = {}, None
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[:1] in (" ", "\t")
        key, sep, value = line.strip().partition(":")
        if indented and current:
            if value:
                fm.setdefault(current, {})[key.strip()] = value.strip().strip("'\"")
        elif sep:
            if key in RECOGNISED and key in fm:
                rep.fail("duplicate recognised frontmatter key %r" % key)
            current = key
            fm[key] = {} if value.strip() == "" else value.strip().strip("'\"")
    return fm


def validate(package: Path, rep: Report) -> dict:
    if not package.is_dir():
        rep.fail("package directory not found: %s" % package)
        return {}

    skill_md = package / "SKILL.md"
    if not skill_md.is_file():
        rep.fail("SKILL.md not found at %s" % skill_md)
        return {}
    text = skill_md.read_text(encoding="utf-8")

    fm = parse_frontmatter(text, rep)
    name = fm.get("name")
    desc = fm.get("description")
    body_end = text.find("---", text.find("---") + 3)
    body = text[text.find("\n", body_end) + 1:] if body_end != -1 else text

    if not name:
        rep.fail("frontmatter missing required field: name")
    elif not NAME_RE.match(name):
        rep.fail("name %r is not lowercase kebab-case (^[a-z0-9]+(-[a-z0-9]+)*$)" % name)
    elif name != package.name:
        rep.fail("name %r must match the package directory %r" % (name, package.name))

    if not desc:
        rep.fail("frontmatter missing required field: description (agents discover "
                 "the skill from it - describe what it does and when to use it)")
    elif len(desc) > 1024:
        rep.fail("description is %d chars (max 1024)" % len(desc))

    compat = fm.get("compatibility") or ""
    if len(compat) > 500:
        rep.warn("compatibility field is %d chars (max 500)" % len(compat))

    if len(body) > 20000:
        rep.warn("SKILL.md instructions are %s chars (>20,000; Microsoft sandbox "
                 "guidance for skill instructions)" % f"{len(body):,}")
    if body.count("\n") + 1 > 500:
        rep.warn("SKILL.md body exceeds 500 lines; move detail into references/")

    unresolved = re.findall(
        r"\{\{(?!\s*[A-Za-z])|\{\{\s*[A-Za-z][\w .\-]{0,62}\s*$", body, re.M
    )
    if unresolved:
        rep.warn("possible unbalanced {{ placeholder in SKILL.md body")

    # Referenced relative paths must exist
    for ref in set(m.strip().replace("\\", "/") for m in REF_RE.findall(body)):
        if not (package / ref).exists():
            rep.fail("SKILL.md references missing file: %s" % ref)

    # File census (skip build caches and VCS dirs)
    files = [
        p for p in package.rglob("*")
        if p.is_file()
        and p.name != "SKILL.md"
        and "__pycache__" not in p.parts
        and ".git" not in p.parts
        and p.suffix.lower() != ".pyc"
    ]
    if len(files) > 349:
        rep.warn("package has %d files (>350 max per skill across agent)" % len(files))
    total = 0
    for p in files:
        rel = p.relative_to(package)
        size = p.stat().st_size
        total += size
        depth = len(rel.parts) - 1
        if depth > 3:
            rep.fail("%s nested deeper than 3 directories" % rel)
        if size > 25 * 1024 * 1024:
            rep.fail("%s is larger than 25 MB" % rel)
        ext = p.suffix.lower()
        if ext in FORBIDDEN_EXTS:
            rep.fail("%s: %s files are not supported by the Microsoft Copilot "
                     "skill sandbox (allowed scripts: %s)" %
                     (rel, ext, ", ".join(sorted(ALLOWED_SCRIPT_EXTS))))
        if ext in ALLOWED_SCRIPT_EXTS and not rel.as_posix().startswith("scripts/"):
            rep.warn("%s looks like a script but lives outside scripts/" % rel)
        if ext and ext not in ALLOWED_SCRIPT_EXTS and ext not in ALLOWED_RESOURCE_EXTS:
            rep.warn("%s: extension %s is not on the documented resource/script list" %
                     (rel, ext))
        if p.suffix.lower() in (".py", ".js", ".ts", ".sh"):
            src = p.read_text(encoding="utf-8", errors="ignore")
            hit = NO_NET.search(src)
            if hit:
                rep.warn("%s mentions %r - the skill sandbox has NO network access; "
                         "remove runtime network/package dependencies" % (rel, hit.group(0).strip()))
            t = TODO_RE.search(src)
            if t:
                rep.warn("%s contains %r marker" % (rel, t.group(1)))

    if total > 50 * 1024 * 1024:
        rep.warn("package totals %.1f MB (Agent Builder zip limit is 50 MB)" % (total / 1e6))

    stats = {"files": len(files) + 1, "bytes": total, "body_chars": len(body)}
    return stats


def make_zip(package: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(package.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(package).as_posix())
    print("Zip staged for upload: %s (%.2f MB)" % (target, target.stat().st_size / 1e6))


def main(argv):
    args = [a for a in argv[1:] if a != "--strict"]
    strict = "--strict" in argv[1:]
    if len(args) not in (1, 3) or "--zip" not in argv:
        if len(args) >= 1:
            package = Path(args[0])
            target = None
        else:
            print(__doc__)
            return 2
    else:
        package = Path(args[0])
        idx = args.index("--zip") if "--zip" in args else None
        target = Path(args[idx + 1]) if idx is not None and idx + 1 < len(args) else None

    if not package.is_dir():
        print("ERROR: not a directory: %s" % package)
        return 2

    rep = Report()
    stats = validate(package, rep)
    fails, warns = rep.summary()
    print("Package: %s" % package)
    print("Stats: %s" % stats)
    for level, msg in rep.findings:
        if level == "WARN":
            print("  WARN  %s" % msg)
        else:
            print("  FAIL  %s" % msg)
    if target:
        make_zip(package, target)
    if fails:
        print("RESULT: FAIL (%d fail / %d warn)" % (fails, warns))
        return 3
    if warns and strict:
        print("RESULT: FAIL under --strict (%d warn)" % warns)
        return 1
    print("RESULT: PASS%s" % ("" if not warns else " (with %d warning(s))" % warns))
    return 1 if warns else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
