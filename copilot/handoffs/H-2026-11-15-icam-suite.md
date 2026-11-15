# Handoff contract — H-2026-11-15-icam-suite

| Field | Value |
| ----- | ----- |
| Requester | Zane West (workspace owner) |
| Executor | copilot-skill-forge (this agent) |
| Reviewer (QA gate) | subagent — general, findings-only |
| Created | 2026-11-15 |
| Status | ready-for-handover (published pending user confirmation) |

## Task

Build a Copilot Studio skill package that guides GAWB leaders through an
MPR-INT-0214-conformant ICAM investigation and outputs the **full ICAM artefact
suite** into the organisation's controlled template `WHS-TMP-0207 Incident
Investigation Report` (DOTX), plus supporting artefacts, styled to the GAWB
Design & Brand Guidelines. Chart-style artefacts are generated as PNG images by
a deterministic script and embedded in the DOCX outputs.

## Intake decisions (user-confirmed 2026-11-15)

1. Primary report template: **GAWB WHS-TMP-0207 DOTX** (SWS 2026 V5 DOCX is
   reference-only, not filled by the skill).
2. Artefact suite: **full GAWB suite** — scoping/investigation plan, PEEPO
   evidence log, timeline chart, 5-Whys, Appendix C Analysis of Contributory
   Factors, ICAM chart, Corrective Action Plan (CAP), and the report.
3. Chart format: **script-generated PNGs** embedded in DOCX outputs.
4. Target surface: **Copilot Studio skill package** (SKILL.md + scripts +
   references + assets; zip for upload) **plus** Studio parent-agent
   instructions.

## Inputs

| Input | Where | Notes |
| ----- | ----- | ----- |
| WHS-TMP-0207 Incident Investigation Report.dotx | `C:\Users\zane_\OneDrive\09 - Agent\Delta\Artefacts\icam\Incident Investigation Report.dotx` (user-provided local copy; SharePoint URL to be recorded in data contract when supplied) | byte-exact copy into assets/templates |
| MPR-INT-0214 Incident Investigation Procedure v3 (Sep 2025) | same folder, PDF | controlling procedure; Appendix C taxonomy; Appendix D form; timeframes |
| MPR-INT-0102 Incident Management Procedure v3 | same folder, PDF | classification L1–L5, triggers, LPP |
| GAWB Risk Matrix (MPR-INT-0272/0090) | `09 - Agent\Delta\Artefacts\risk\GAWB Risk Matrix.pdf` | consequence levels 1–5 |
| Design and Brand Guidelines (2017) | `09 - Agent\Delta\Skills\docx\references\Design and Brand Guidelines.pdf` | colours #007CBB/#00A98F + palette, Ubuntu/Verdana, wave element, voice |
| Safety Wise flowcharts / interview guidelines / HSEC procedure | Downloads | methodology reference only |
| InvestigatePro ICAM toolkit (2026) | Downloads | methodology reference only |
| Sample incident INC-0000812 (closed, security type) | `Artefacts\icam\Incident_INC-0000812_20261022_1035.pdf` | smoke-test data source; **test data only, labelled sample** |
| Prior instruction sets (draft `ICAM Assistant.md`, `gawb-icam-investigation-agent-instruction-set.md`) | `09 - Agent\Delta` | content base to merge |

Scope boundary: the executor produces artefacts only. No tenant upload, no
publishing, no contact with the tenant. The SWS 2026 V5 template is never
filled. No fabricated investigation content in shipped assets — sample data is
synthetic/derived from the closed sample incident and clearly labelled.

## Deliverables

| Path | Description | Version |
| ---- | ----------- | ------- |
| .opencode/skills/gawb-icam-investigation/ | skill package (SKILL.md, scripts/, references/, assets/) | v0.1.0 |
| copilot/uploads/gawb-icam-investigation-v0.1.0.zip | upload artefact | — |
| copilot/agents/gawb-icam/parent.instructions.md | Studio parent-agent instruction set | v0.1.0 |

## Acceptance checklist

- [x] `validate-package.py` passes with no FAIL (WARNs explicitly judged) —
      PASS, exit 1 (warn-only); sole WARN = `.dotx` extension, judged
      **by design**: the byte-exact controlled template ships as a data
      asset, not a runnable resource (SHA256 verified at build and by QA)
- [x] SKILL.md description triggers test prompts worded like real user asks
- [x] Scripts: allowed extensions, no network/package installs, positional args
- [x] PNG chart script proven: renders branded timeline / 5-Whys / ICAM chart /
      PEEPO chart PNGs with stdlib only, verified visually
- [x] Report build proven end-to-end on WHS-TMP-0207 with sample data: all
      58 SDT controls in `word/document.xml` audited; fill audit reports
      39/39 fill items, `missing: []`; dropdowns filled, dates set, all four
      charts embedded; verified page-by-page over all 16 rendered pages
- [x] Every suite artefact generated and opened/verified (plan, evidence
      log incl. new §4 PEEPO entries, appendixc, cap, witness — all exit 0)
- [x] No secrets / tenant URLs / personal data embedded (sample uses
      synthetic names; template's inherent core.xml author metadata
      [Leslie Sheremeta / Zane West] flagged for user judgement — inherent
      to the byte-exact controlled template)
- [x] Parent instructions pass the 9-practice checklist + test-plan minimum
- [x] Registry rows updated with validation result

## Validation log

| # | Check | Command | Result |
| - | ----- | ------- | ------ |
| 1 | Report build + fill audit | `python build_report.py assets\samples\incident-sample.json <charts> report-sample.docx audit` | exit 0; filled=39, missing=[] |
| 2 | Report render (Word COM → PDF → PNG, all pages) | `render.ps1 -DocPath report-sample.docx` | 16 pages; title, checkboxes, factors, recs/learnings numbering, PEEPO+ICAM+timeline+5whys charts, CAP, photos, appendices, team, approval conditions box all verified |
| 3 | Chart renders | `python render_charts.py incident-sample.json <charts>` | exit 0; 4 PNGs rendered |
| 4 | Artefact builds ×5 | `python build_doc.py <plan\|evidence\|appendixc\|cap\|witness> …` | exit 0 each; evidence log re-rendered and visually verified (banner, register, checklist, coverage check with auto Evidence IDs, §4 entries) |
| 5 | Package lint | `python validate-package.py <pkg> --zip copilot\uploads\gawb-icam-investigation-v0.1.0.zip` | PASS with 1 judged WARN (.dotx by design); zip staged 654 KB / 14 files |
| 6 | QA gate (findings-only subagent) | checklist items a–g | all PASS; 4 findings folded back (1 WARN fixed: stage-tracker example; 3 INFO: Python floor aligned to 3.8+, contract SDT count corrected 56→58, stale HF comment in build_doc.py corrected) |
| 7 | Post-fix regression rebuild | artefacts ×5 + report audit + re-lint + re-zip | exit 0 ×6; PASS with judged WARN; zip re-staged |

## QA findings (findings-only return)

1. **[WARN — FIXED]** `parent.instructions.md` stage-tracker example said
   "Stage 3 of 7 — Contributing factor analysis"; corrected to Stage 5 of 7.
2. **[INFO — FIXED]** SKILL.md claimed Python 3.9+, scripts claim 3.8+ (no
   3.9-only syntax verified); aligned SKILL.md to 3.8+.
3. **[INFO — FIXED (here)]** Contract required "all 56 SDT controls";
   actual template has 58 SDTs in `word/document.xml` (plus 2 in
   footer1.xml). Checklist corrected.
4. **[INFO — FIXED]** Stale `build_doc.py` comment about HF14+ numbering
   corrected; taxonomy.md already asserted the verified numbering.

## Pending user items

- SharePoint source URL for WHS-TMP-0207 (record in data contract when
  supplied; package currently documents the local-provided source and the
  byte-exact SHA256).
- Judgement on the template's inherent core.xml author metadata (ships with
  the controlled template; byte-exact copy is required, so it is retained).


## Hand-back

- User reviews delivery summary, opens sample output pack, then uploads the zip
  to Copilot Studio (Build tab → Add skill → upload) and pastes the parent
  instruction set into their agent.
