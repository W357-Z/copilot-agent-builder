---
name: org-document-suite
description: Fill the organisation's managed Word, PowerPoint and Excel templates with structured data to produce final documents. Use whenever a report, letter, briefing or dashboard must be generated in organisation template format, when data must be placed into a managed template, or when checking which placeholders a template expects.
license: internal-use
compatibility: Requires python3 (or `py -3` on Windows). Stdlib only; no network access needed.
metadata:
  author: copilot-skill-forge
  version: "1.0.0"
  surfaces: Copilot Studio (GitHub Copilot harness), Microsoft 365 Copilot declarative agents, local coding agents
---

# org-document-suite

Generate final documents from the **organisation's official templates** instead of
letting a model invent layout. The heavy lifting is done by `scripts/fill-template.py`,
which is stdlib-only and therefore runs locally and inside the Microsoft Copilot
skill sandbox.

## Templates

- Template files live in `assets/templates/` (local copies kept up to date from
  the organisation's SharePoint/OneDrive library).
- Read `references/data-contract.md` **before** generating with a template for
  the first time. It lists available templates, their placeholder tokens and
  which SharePoint file to sync from.
- Never regenerate or "fix" the visual design of a template. Only fill tokens.

## Workflow

1. **Confirm the task.** Identify: template type (`.docx`, `.pptx`, `.xlsx`),
   output location and file name, and the data (from the user, a JSON file, or
   extracted workspace files).
2. **Inspect the template** if its tokens are unknown:
   ```
   python3 scripts/fill-template.py assets/templates/<name>.docx <(echo {}) out.docx --audit
   ```
   `--audit` prints every `{{Token}}` in the template and what is missing — no
   output is written.
3. **Build `data.json`** (flat map, string values) with exactly the tokens the
   audit listed follow the token naming rules in `references/data-contract.md`.
4. **Fill the document:**
   ```
   python3 scripts/fill-template.py assets/templates/<name>.docx data.json output/<client>_report_2026-11-08.docx
   ```
5. **Verify.** Exit code 0 = all tokens filled. Exit 3 = missing tokens left
   intact; read the JSON report, correct the data, re-run. Always confirm with
   the user before the file is sent anywhere.
6. **Record** the run in the coordinator's registry (path supplied by the
   coordinating agent) when this skill runs as part of a handoff contract.

## Scripts

| Script | Purpose |
| ------ | ------- |
| `scripts/fill-template.py` | Fill `{{Token}}` placeholders in `.docx`/`.pptx`/`.xlsx`, auto-merging placeholders that Word split across runs |

CLI: `fill-template.py <template> <data.json> <output> [--audit]` — positional
arguments so the skill sandbox can run it without a shell.

## Guardrails

- **Never edit** `assets/templates/` masters in place; they must remain byte-exact
  copies of the SharePoint source for audit purposes.
- **Never embed** SharePoint credentials, tenant names or full internal URLs in
  data files or output documents.
- If the task needs content the template has no token for, stop and ask the
  user (or coordinating agent) instead of inventing extra sections.
- Values must be single-line strings; newlines become spaces (v1 limitation,
  documented in `references/data-contract.md`).
