# Data contract — org-document-suite

## Template sources (SharePoint / OneDrive)

Download current template copies into `assets/templates/` and keep this table
updated whenever the organisation republishes a template.

| Template file | Format | SharePoint source (recorded, not embedded) | Last synced | Owner |
| ------------- | ------ | ------------------------------------------- | ----------- | ----- |
| `_placeholder-docx.docx` | Word | *(paste SharePoint URL here — used for lookup only, never embedded in outputs)* | — | — |
| `_placeholder-pptx.pptx` | PowerPoint | *(URL)* | — | — |
| `_placeholder-xlsx.xlsx` | Excel | *(URL)* | — | — |

Sync procedure

1. Open the SharePoint document library (or OneDrive folder) named by the
   coordinating agent or the user.
2. Download the template to `assets/templates/`, keeping its official name.
3. Update the table above (date + owner) — the full URL is documentation, the
   scripts never fetch from it automatically because the skill sandbox has no
   network access.

## Placeholder syntax

- `{{TokenName}}` — also accepts `{{token_name}}` and `{{client-name}}`
  (letters, digits, spaces, hyphens, dots, underscores, 1–64 chars total).
- Templates must keep each token inside one paragraph / shape / cell; runs may
  split it and the script re-merges, but do not split tokens across two
  paragraphs.

## Data file (`data.json`)

```json
{
  "ClientName": "Northwind Ltd",
  "ReportDate": "2026-11-08",
  "PreparedBy": "Reports Team",
  "TotalSlots": "42",
  "EscalationContact": "pmo@org.example"
}
```

Rules

- **Flat object, string values only.** `null` behaves like a missing key.
- Newlines in values become spaces (single-line v1).
- Values must not contain `{{...}}` sequences.
- Numbers are written as text — the template's number formatting renders them.
- Dates use ISO `YYYY-MM-DD`; the template displays its own format.
- Empty string `""` is valid and clears the token.

## Behaviour of fill-template.py

| Condition | Result |
| --------- | ------ |
| All tokens found in data | output written, exit 0 |
| Token missing from data | token left intact in output, JSON report + exit 3 |
| Key in data with no token in template | reported as `unused_data_keys` (likely typo) |
| Token split across XML runs (edits in Word) | re-merged automatically, then filled |
| Template changed since last sync | re-download; the script only reads template bytes |

## Reported JSON (stdout)

`filled_count`, `missing_in_data`, `unused_data_keys`, `left_in_output`,
`parts_filled`, `warnings` — HISTORY feeds the handoff contract's
"Validation" section when tests run under a coordinator.
