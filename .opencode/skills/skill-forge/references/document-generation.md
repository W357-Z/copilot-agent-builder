# Document generation from organisation templates

Working standard for skills that produce `.docx` / `.pptx` / `.xlsx` documents
from managed templates. Reference implementation: `org-document-suite`
(neighbouring skill) — copy and adapt it rather than inventing a different
convention.

## Principles

1. **Templates are assets, not code.** The model fills tokens; it never
   re-creates layout, styling or branding.
2. **Deterministic scripts over prose.** Generating a file is done by a script
   so the same inputs always give the same output.
3. **No network in scripts.** SharePoint/OneDrive sources are consumed by the
   human or the wider agent through downloads; sandbox scripts work on local
   copies only.
4. **Fail loudly, leave partially valid output.** Missing tokens stay as
   `{{Token}}` in the output; exit codes tell the caller what happened. The
   agent then asks the user rather than inventing content.

## Placeholder contract

- Syntax `{{TokenName}}` (1–64 chars; letters, digits, spaces, hyphens, dots,
  underscores) placed by the template owner in Word/PowerPoint/Excel.
- Templates keep each token inside one paragraph/shape/cell. Word splitting a
  token across XML runs is tolerated (the script re-merges), splitting across
  paragraphs is not.
- Token names are stable product vocabulary; document the full set per template
  in the skill's `references/data-contract.md` with sample values.

## Data contract

- `data.json`: flat object, string values, single-line (newlines → spaces).
- ISO dates; numbers as strings; `""` clears a token; `null` = missing.
- Values must not contain `{{…}}`.
- Constant/boilerplate tokens (e.g. `{{ReportPeriod}}`) may be prefilled by the
  agent from context only when the source is unambiguous; otherwise ask.

## Script shape (positional args, sandbox-friendly)

```
python3 scripts/fill-template.py <template> <data.json> <output> [--audit]
```

Implemented behaviour to preserve when adapting:

- Word parts: `word/document.xml`, headers/footers, footnotes, endnotes.
- PowerPoint parts: slides, layouts, masters, notes.
- Excel parts: shared strings + inline strings on sheets (not chart labels).
- Text-node surgery only: byte-identical zip output for untouched parts;
  template byte order and compression preserved.
- Values XML-escaped on insertion.

## Audit first, then fill

`--audit` prints the token inventory and data gaps without writing files. The
standard loop: audit → build data.json → fill → verify exit code → show the
final path to the user. For repeated runs, keep `data.json` under the task's
`copilot/handoffs/` artefacts so a QA reviewer can re-run the fill.

## Extending (v2 candidates, only on demand)

Repeating table rows (`{{#each}}`-style), multi-line values, Excel numeric
cells, chart labels. Implement only when the org templates actually need them;
keep stdlib-only and update the data contract.
