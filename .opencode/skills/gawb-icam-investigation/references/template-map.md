# Template map — WHS-TMP-0207 Incident Investigation Report

How `build_report.py` fills the controlled GAWB template
(`assets/templates/Incident Investigation Report.dotx`, byte-exact copy,
SHA256 `D0332EE6BF26C74350672A44F1E038623DF030B50EF2B7067679172E5B6C0434`).
Re-audit this map whenever the organisation re-issues the template: re-sync
the asset, re-run the SDT audit, and re-verify heading-scope names before
trusting fills.

## Template anatomy (58 SDTs, 16 rendered pages)

| Report section | Fill mechanism |
| -------------- | -------------- |
| Cover + Version History + Document History + About | Template chrome — untouched except core property `dc:title` |
| 3.1 Assumptions and Exclusions | Heading-scoped SDT (`assumptions`) |
| Incident Details table | 14 cell SDTs filled positionally (label `tc` + value SDT wrapping a `tc` per row); Yes/No checkboxes are ☐/☒ glyph SDTs |
| Incident Description | Paragraph SDT (`incident.description`) |
| 4.2 Injury / Damage / Impact | Paragraph SDT (`incident.injuries`) |
| Immediate Actions Taken | Paragraph SDT (`incident.immediate_actions`) |
| Basic Causes | Paragraph SDT (`basic_cause`) |
| 5.2.1–5.2.4 ICAM categories | Four heading-scoped SDTs (`factors.*`, one per category, line-broken per factor) |
| §7 Recommendations | Multi-paragraph SDT with built-in list numbering — fill with `multi_lines(..., numbered=False)` so Word numbers once (v1 double-numbered) |
| §8 Key Learnings | Same pattern (`numbered=False`) |
| §9 Conclusions | Paragraph SDT |
| §10 PEEPO section | PEEPO chart PNG after the section note; `peepo_note(auto)` fills the note |
| §11 Timeline & 5-Whys | `icam-timeline.png` + `icam-5whys.png` after the section note; `timeline_note(auto)` |
| §12 Photos | Repeating row: 2 cells × [image-SDT, description-SDT] |
| §13 Appendices | Repeating row: [plain ID `tc`, name, reference, date, type-list SDT] |
| §14 Investigation Team | Repeating row: [name-SDT, role-SDT, plain signature `tc` (left blank for wet signing), date-SDT] |
| §15 Approval | Repeating row (same shape as Team) + **conditions box = last SDT of the heading scope** "Approval of Investigation Report" (SDT #58) |

## Fill strategy (why not global SDT indexes)

1. **Heading-scoped SDT discovery** — `heading_scopes()` walks direct body
   children between Heading-style paragraphs; `scope_map`/`scope_sdts` grab
   the SDTs in each scope. Fills are keyed by heading text, not by global SDT
   index, so a template edit that inserts/removes an SDT upstream does not
   silently corrupt fills.
2. **Repeating sections unwrapped** — CAP/Photos/Appendices/Team/Approval
   data rows sit inside `repeatingSection > sdtContent >
   repeatingSectionItem > sdtContent > tr > cell-SDTs`. The builder unwraps
   the wrapper to plain `tr`s, clones the last template row per data item,
   then fills cells via `effective_cells()` (resolving nested cell SDTs).
3. **Placeholders resolved** — template runs carry `rStyle="PlaceholderText"`
   and grey `w:color`; `fill_sdt`/`fill_plain_paragraph` strip both, and
   `_clear_placeholder_state` removes `<w:showingPlcHdr/>`. A final pass
   (`strip_resolved_placeholders`) removes flags from SDTs whose text is now
   real content (placeholder-looking text keeps its flag).
4. **Serialisation** — `L.serialise_preserving_root(doc, original_bytes)`
   keeps namespace declarations an ElementTree round-trip would drop.

## Known Word-fidelity traps (do not "simplify" these away)

- **`docProps/core.xml` string surgery.** The Title cell SDT is data-bound to
  `/ns1:coreProperties[1]/ns0:title[1]`; Word overwrites the visible text
  from core.xml on open. The builder patches `dc:title` by regex string
  replacement (XML-escaped), *not* ElementTree: an ET round-trip loses the
  `dcterms` prefix declaration used by `xsi:type="dcterms:W3CDTF"` and Word
  then reports the file as corrupted.
- **Content type.** `[Content_Types].xml` must declare
  `wordprocessingml.document.main+xml` (not `.template.main+xml`) or Word
  refuses the file; the builder patches this after loading the DOTX.
- **Built-in list numbering.** §7/§8 SDTs carry Word list numbering: pass
  `numbered=False` so the builder doesn't print "1." prefixes (which double-
  number).
- **Dropdowns have empty option lists** in the template — any value is
  acceptable; fill as plain text.

## Chart embedding

Chart PNGs are embedded after their section anchors only if the file exists
in the charts directory; missing PNGs are listed in the `missing` audit array
(never silently skipped). Render with `render_charts.py` first:
`icam-chart.png` after §5.2.4, `peepo-chart.png` after §10 note,
`icam-timeline.png` + `icam-5whys.png` after §11 note.

## CLI contract

```
python build_report.py <data.json> <charts_dir> <out.docx> [audit]
```

Exit codes: 0 ok · 2 usage · 3 data/template error · 1 unexpected. `audit`
prints a JSON fill report (`filled`, `missing`, `out`) instead of exiting
quietly — always build with `audit` when verifying a new data file.

## Verification workflow (outside the skill)

To eyeball the rendered result on Windows without shipping tooling:
Word COM export to PDF, then WinRT PDF rasterisation to per-page PNGs
(see the skill's review notes; keep `Add-Type` per process, single-quoted
`IAsyncOperation`1` strings, `$env:PYTHONIOENCODING="utf-8"`). Trust the PDF
page count, not Word's `ComputeStatistics`.
