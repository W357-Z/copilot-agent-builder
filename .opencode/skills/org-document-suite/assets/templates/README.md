# assets/templates — managed template copies

This folder holds **local copies** of the organisation's official templates so
that `scripts/fill-template.py` can work with them (the skill sandbox has no
network access, and scripts never fetch from SharePoint for you).

## Intake

1. Download each template from the organisation's SharePoint/OneDrive library
   in its current shape (do not re-save from Word/PowerPoint in a different
   format unless the template owner says so).
2. Keep the official file name (for example `Client-Report-A4.docx`).
3. Register it in `references/data-contract.md` (source URL, sync date, owner).
4. Confirm with the template owner that `{{TokenName}}` placeholders are in
   place; if the template has no tokens yet, request that the owner adds them
   rather than editing the master yourself.

## Integrity

- Treat these files as **read-only masters**. `fill-template.py` reads them and
  writes a new output file; it never modifies a template.
- Overwrite a copy only to bring it in sync with a freshly republished
  SharePoint version, then update the data contract table and re-run the
  `--audit` step to learn the token set.
