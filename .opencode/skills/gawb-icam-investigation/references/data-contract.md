# Investigation data contract (`incident.json`)

One JSON file drives every artefact: the report (`build_report.py`) and the
five standalone documents (`build_doc.py` plan | evidence | appendixc | cap |
witness) plus the charts (`render_charts.py`). A schema-defining sample lives
at `assets/samples/incident-sample.json` — synthetic data only; replace every
value with case facts. Scripts read keys tolerantly (missing optional keys
render as blanks or are skipped); required keys raise a data error (exit 3)
with the key name in the message.

## Top-level sections

| Key | Required by | Type | Notes |
| --- | ----------- | ---- | ----- |
| `meta` | all | object | Report/classification chrome — see below |
| `incident` | all | object | Core incident facts — see below |
| `assumptions` | report §3.1 | string | Assumptions and exclusions narrative |
| `basic_cause` | report §6 | string | The basic cause statement |
| `factors` | report §5, appendixc, icam chart | object | ICAM analysis, four lists |
| `peepo` | report §10, peepo chart, evidence artefact | object | PEEPO classification, five lists |
| `conclusions` | report §9 | string | Conclusions narrative |
| `recommendations` | report §7, cap artefact | list of objects | `text` + optional `control_type` |
| `learnings` | report §8 | list of strings | Key learnings (one paragraph each) |
| `cap` | cap artefact, report CAP table | list of objects | `recommendation`, `dept`, `person`, `due` |
| `timeline` | timeline chart | list of objects | `time`, `event`, `source` |
| `fivewhys` | 5-whys chart | list of objects | `question`, `answer` |
| `evidence` | evidence artefact, report §10/§11 | list of objects | Evidence register rows — see below |
| `plan` | plan artefact | object | `scope`, `objectives`, `team`, `method`, `timeframe_days`, `due_date`, `lpp`, `approval_path` |
| `witness` | witness artefact | object | `name`, `occupation`, `date_time`, `location`, `statement` (required — artefact fails without it) |
| `team_members` | report §14 table | list of objects | `name`, `role`, `date` (signature cell left blank for wet signing) |
| `approval` | report §15 | object | `name`, `role`, `date`, `conditions` (multi-line string for the approval-conditions box) |
| `appendices` | report appendices table | list of objects | `name`, `reference`, `date`, `type` |
| `photos` | report photos table | list of objects | `description`; `image` = optional file path, embedded if the file exists |

## `meta`

```json
"meta": {
  "report_no": "GAWB-INV-2026-001",
  "classification": "Level 3 - Medium consequence / Moderate potential",
  "privileged": false,
  "prepared_date": "2026-10-22"
}
```

`classification` drives mandatory-ICAM notes and timeframe defaults in the
plan artefact (Level 4 / Level 5 detection is a substring match). `privileged`
flags LPP status for the plan; the investigation decision itself belongs to
ELT and Corporate Counsel — never infer it.

## `incident`

| Field | Report field |
| ----- | ------------ |
| `title` | Incident Title (also written to the core document property `dc:title` — the cell SDT is data-bound to it) |
| `type` | Incident Type |
| `date`, `time` | Date / Time of incident |
| `inx_ref` | INC / SAI360 reference |
| `risk_actual`, `risk_potential` | Risk (Actual) / Risk (Potential) |
| `involved_parties` | Persons / plant involved |
| `building`, `location` | Building / Area, Location |
| `activity_type` | Activity being performed |
| `risk_assessment` | Risk assessment in place |
| `standard_controls` | Existing standard controls in place (Yes/No) |
| `standard_ref` | Reference (procedure / SWMS / JSA) |
| `description` | Incident Description narrative |
| `basic_event` | The basic event sentence (ICAM chart header; falls back to `description`) |
| `injuries` | Details of Injury / Damage / Impact |
| `immediate_actions` | Immediate Actions Taken by Management |

## `factors` (ICAM, Appendix C)

```json
"factors": {
  "absent_failed":     [ { "code": "DF1", "text": "...", "rating": "Absent",
                           "reason": "..." } ],
  "individual_team":   [ { "code": "IT10", "text": "...", "reason": "..." } ],
  "task_env":          [ { "code": "WF5", "text": "...", "rating": "Significant",
                           "reason": "..." } ],
  "organisational":    [ { "code": "RM", "text": "...", "reason": "..." } ]
}
```

Codes come from `taxonomy.md` (DF/IT/WF/HF/OR sets). `rating` is optional
(category scale applies when omitted); `reason` is the evidence-linked why —
required in substance even where the key is optional. Each list renders as a
separate report SDT (§5.2.1–§5.2.4), the Appendix C worksheet and the ICAM
chart columns.

## `peepo` (classification of contributing factors)

```json
"peepo": {
  "people":        [ { "text": "...", "ref": "E-02" } ],
  "environment":   [ { "text": "...", "ref": "E-01" } ],
  "equipment":     [ { "text": "...", "ref": "E-01" } ],
  "procedures":    [ { "text": "...", "ref": "E-03" } ],
  "organisation":  [ { "text": "...", "ref": "E-03" } ]
}
```

Distinct from `factors`: PEEPO classifies *where information came from and
what it concerns*; ICAM `factors` classifies *why the event happened*.
Entries are `{text, ref}` objects or plain strings; `ref` cross-references the
`evidence` register ID and renders on the chart box (grey, right-aligned) and
in the evidence artefact's coverage check. All five lists are optional; an
empty section renders an empty chart column.

## `evidence` register

```json
{ "id": "E-01", "description": "...", "type": "Digital",
  "source": "Worker mobile device", "status": "Fact",
  "location": "Event Management System attachments",
  "collected_by": "...", "collected_at": "2026-01-07" }
```

`status` is `Fact` (directly observed or verifiable) or `Assumption` (must be
resolved before the analysis is finalised). IDs are referenced by `peepo.*.ref`
and `timeline[].source` where applicable.

## Rules of engagement

- Never fabricate: unknowns become data gaps in `assumptions` or parked
  assumptions in `evidence` with `status: "Assumption"`.
- Personal data: collect names only as needed for the artefacts; the shipped
  sample uses synthetic names and must not be re-used as real content.
- Keep `text` fields in fact-finding language (no blame phrasing); the
  taxonomy check questions in `taxonomy.md` keep factors anchored.
- Charts render only for sections that exist (`render_charts.py` exits 3 and
  lists skipped charts when a section is missing — that is the signal the
  data is incomplete, not a reason to hand-stub values).
- One JSON file per investigation; keep it under version control alongside
  the artefacts (ECM/SAI360 storage rules apply to the outputs).
