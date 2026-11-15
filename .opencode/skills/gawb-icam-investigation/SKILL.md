---
name: gawb-icam-investigation
description: Guides a GAWB ICAM investigation per MPR-INT-0214 and produces the full artefact suite - investigation plan, PEEPO evidence log, timeline and 5-Whys charts, Appendix C analysis of contributory factors, ICAM chart, corrective action plan, witness statements, and the final report filled into the controlled WHS-TMP-0207 template. Use when the user is running an incident or near-miss investigation, asks for ICAM or PEEPO analysis, wants to classify contributory factors, needs interview or witness-statement support, or asks to generate, fill or update the incident investigation report or corrective action plan. Triggers- incident investigation, ICAM, PEEPO, 5 Whys, contributory factors, absent or failed defences, witness statement, corrective action plan, WHS-TMP-0207, investigation report, notifiable incident.
license: internal-use
compatibility: Requires Python 3.8+ (or the `py -3` launcher on Windows). Stdlib only; no network, no package installs.
metadata:
  author: GAWB H&S Systems (built with skill-forge)
  version: "0.1.0"
  surfaces: Copilot Studio (GitHub Copilot harness and standard harness)
---

# gawb-icam-investigation

ICAM investigation artefact suite: charts + five standalone documents + the
controlled-template report, all driven by one investigation data file.

## When to use

- "Help me run an ICAM investigation for this incident."
- "Can you draft the PEEPO evidence log / witness statement template?"
- "Classify these findings into contributory factors."
- "Fill in the WHS-TMP-0207 incident investigation report."
- "We need a corrective action plan from the investigation findings."
- "Do we need an ICAM for this?" (level/LPP triage)

## Prerequisites (intake)

Before generating anything, confirm from the user or case file:

1. **Incident basics** — what happened, where, when, who was involved.
2. **Classification** — actual and potential consequence (e.g. "Level 3 -
   Medium consequence / Moderate potential"). If the user doesn't know, work
   through `references/workflow.md` Stage 0 with them; never invent a level.
3. **LPP status** — determined by ELT and Corporate Counsel. If unknown, ask;
   never decide it yourself, and never mark a document privileged on your own.
4. **Output directory** — where artefacts and charts go.
5. **Investigation data file** — the JSON matching
   `references/data-contract.md`. Build it interactively with the user when
   it doesn't exist; start from `assets/samples/incident-sample.json` as the
   structural example (synthetic data only - never reuse its content).

Missing inputs → ask. Do not guess facts, names, dates or classifications.

## Workflow

1. **Prepare** — read `references/data-contract.md` (schema) and
   `references/workflow.md` (process, triggers, timeframes). For factor
   classification read `references/taxonomy.md`; for interviews read
   `references/interview-guide.md`. Read the relevant reference before the
   corresponding conversation stage - never from memory.
2. **Charts** — once `timeline`, `fivewhys`, `factors` or `peepo` data
   exists:

   ```
   python3 scripts/render_charts.py <investigation.json> <charts_dir>
   ```

   Exit `3` means a data section was missing (the JSON report names it) -
   that is a signal to gather data with the user, not to fabricate entries.
3. **Artefacts** — build any of the five standalone documents as data
   becomes ready (they are independent; build on demand):

   ```
   python3 scripts/build_doc.py <plan|evidence|appendixc|cap|witness> <investigation.json> <out.docx> [charts_dir]
   ```

4. **Report** — when the analysis is complete and the user approves:

   ```
   python3 scripts/build_report.py <investigation.json> <charts_dir> <out.docx> audit
   ```

   Pass `audit` to get a JSON fill report. Exit `0` with an empty
   `missing` array is the success bar; any `missing` entry names the data
   key or chart to fix, then rebuild.
5. **Verify** — exit-code table for all three scripts:
   `0 = success · 2 = usage error (check arguments) · 3 = data/template
   issue (fix the named key or chart) · 1 = unexpected (report the failure
   verbatim to the user; do not retry blindly)`.
6. **Hand back** — list artefact paths produced, the charts embedded, any
   warnings from the audit report verbatim, and the user's remaining
   procedural steps (approval path, SAI360/ECM upload - humans do those).

## Operating rules during the conversation

- **Fact-finding, not fault-finding.** Keep language blame-free; guide
  contributory-factor analysis sharp-end to latent (DF/IT → WF/HF → OR) and
  keep asking "why did that make sense at the time?".
- **Statements are not facts.** Witness accounts are validated against
  photos, records and physical conditions before entering the analysis.
- **Every confirmed factor needs a reason.** Ratings come from the taxonomy
  scales; recommendations follow the hierarchy of controls.
- **Unknowns stay visible.** Park them in Assumptions and Exclusions or the
  evidence register with `status: "Assumption"`.
- **The template is the source of truth.** Never edit
  `assets/templates/*.dotx`; the report builder copies it byte-exact and
  fills the copy. Template mechanics and known Word-fidelity traps are in
  `references/template-map.md` - if a fill looks wrong, check there first.
- **Brand** - colours and fonts are fixed in `references/brand-tokens.md`;
  do not restyle outputs.

## Files

| Path | Role |
| ---- | ---- |
| `scripts/render_charts.py` | Renders icam-timeline, icam-5whys, icam-chart, peepo-chart PNGs |
| `scripts/build_report.py` | Fills the controlled WHS-TMP-0207 template into the final report DOCX |
| `scripts/build_doc.py` | Builds the 5 standalone artefacts (plan, evidence log, Appendix C worksheet, CAP, witness statement) |
| `scripts/lib_docx.py` | DOCX/SDT toolkit: placeholder resolution, branded helpers, OOXML save |
| `scripts/lib_png.py` | Pure-Python PNG canvas: brand-coloured charts, no external deps |
| `references/workflow.md` | The 8-stage investigation process, triggers, timeframes, LPP/notifiable/psychosocial disciplines |
| `references/taxonomy.md` | Appendix C contributory-factor codes, check questions, ratings, error/violation types |
| `references/interview-guide.md` | Interview question sets and s4.3.4 conduct rules |
| `references/data-contract.md` | The investigation JSON schema every script reads |
| `references/template-map.md` | WHS-TMP-0207 anatomy, fill strategy, Word-fidelity traps |
| `references/brand-tokens.md` | GAWB colours and typefaces used in outputs |
| `assets/samples/incident-sample.json` | Schema example with synthetic data only |
| `assets/templates/Incident Investigation Report.dotx` | Byte-exact copy of the controlled template |

## Guardrails

- Never edit the controlled template or procedure content; outputs only.
- No network calls, no package installs at runtime (sandbox constraint).
- No secrets, tenant URLs or personal data in scripts or committed files;
  the sample's synthetic names are placeholders, never real content.
- On conflict between this skill and the current controlled issue of
  MPR-INT-0214 / MPR-INT-0102 / WHS-TMP-0207, stop and tell the user -
  procedures win, references are snapshots.
- The skill produces documents; it never approves, submits or notifies.
  Approval, SAI360/ECM upload, regulator notification and distribution are
  human steps per the procedures.
