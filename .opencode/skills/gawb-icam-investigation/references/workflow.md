# GAWB ICAM investigation workflow (MPR-INT-0214)

Grounding for the staged conversation. Sources: MPR-INT-0214 Incident
Investigation Procedure v3 (Sep 2025), MPR-INT-0102 Incident Management
Procedure v3. Verify every requirement against the currently controlled issue
before telling the user "the procedure requires X".

## Purpose statement (use verbatim when users ask why)

Fact-finding, not fault-finding: identify immediate, contributing and root
causes (including psychosocial factors), identify absent or failed controls,
and recommend corrective and preventive actions (MPR-INT-0102 Stage 5). The
aim is not to apportion blame or liability but to identify failures within the
organisation, systems and communication.

## Investigation triggers (MPR-INT-0102 Stage 5)

| Classification | Method |
| -------------- | ------ |
| Not Significant | Informal investigation (checklist) |
| Low / Medium | 5 Whys or equivalent (WHS-TMP-0206); ICAM may be required (relevant leader determines) |
| High / Extreme / Notifiable / Psychosocial Level 3–4 | ICAM mandatory, report in WHS-TMP-0207 |

Psychosocial escalation (MPR-INT-0102 s5): Level 1 emerging hazard, low
distress; Level 2 repeated issues, rising conflict; Level 3 bullying or
harassment allegations, serious distress, potential compensation claim;
Level 4 threats of violence, assault, suicide or self-harm, exposure to
fatality or catastrophic event. The psychosocial level informs the incident
level and the investigation method.

## Timeframes (MPR-INT-0214 Appendix A)

| Classification | ICAM | Completion target |
| -------------- | ---- | ----------------- |
| Level 1 – Not Significant / Level 2 – Low | may be required | 25 working days |
| Level 3 – Medium consequence / Moderate potential | may be required | 25 working days |
| Level 4 – High / Significant potential | required | 30 working days (safety, not under LPP; non-safety and near miss) · 50 working days (safety under LPP) |
| Level 5 – Extreme / Severe potential | mandatory (LPP for safety events) | 60 working days (safety under LPP) · 35 working days (safety near miss; non-safety and near miss) |

Investigator appointment: Level 4–5 mandatory ICAM — from the ICAM list of
investigators; under LPP the ELT and Corporate Counsel determine scope and
whether the investigation is internal or external. Approval path rises from
relevant leader (Level 2) to executive leader + relevant leader (Level 3) to
ELT and Corporate Counsel for safety investigations under LPP.

## Stages

### Stage 0 — Intake, classification and scoping

Confirm: what happened (basic event), where, when, who was involved, actual
and potential consequence (risk matrix wording, e.g. "Level 3 – Medium
consequence / Moderate potential"), INX (SAI360) reference. Then confirm
method trigger, LPP status (determined by ELT + Corporate Counsel — never
decide it yourself), completion date from the table above, team (lead
investigator must be ICAM Lead trained; independent of the area when under
LPP), notification status (internal Appendix A; external regulator via H&S
Manager / Environmental Scientist), site preservation, and immediate actions
already taken. Output: a scoping summary with classification, method, LPP
status, timeframe, team, open questions.

### Stage 1 — Investigation plan (scoping)

Establish scope, timeframes, resources and risks to the investigation
activities (MPR-INT-0214 s4.2.2). Build the PEEPO data-collection plan:
People (witnesses, workers, training, fatigue), Environment (weather, scene,
lighting/visibility/audibility, signage), Equipment (vehicles, plant, tools,
infrastructure, condition and failure signs), Procedures (documents, reports,
charts, maps), Organisation (training, communication, resources, culture,
management). Produce `incident-investigation-plan` artefact.

### Stage 2 — Evidence gathering (PEEPO log)

MPR-INT-0214 s4.3: inspect the site as it was at the time of the incident
(energy sources, equipment condition, loss of containment, control switch
positions, illumination/visibility/audibility, marks and spills, weather,
signage). Photograph with time and location documented; respect the
Information Privacy Act 2009 (explain reason, scope, storage, access for
private information including images). Chain of custody only when Corporate
Counsel directs: photograph each item, record location, recovery time/date,
description, condition, unique markings; quarantine failed components, tag
"out of service", keep an itemised log. Every register item carries status
**Fact** (directly observed or verifiable) or **Assumption** (must be resolved
before the analysis is finalised). Produce `peepo-evidence-log` artefact.

### Stage 3 — Interviews and witness statements

Interview people present at the time, the initial responders, and those who
operate, maintain or manage the relevant machinery, processes or projects.
Statements are verbal accounts, **not facts** — validate against photos,
records and physical conditions. Interview rules (s4.3.4): in private, free of
interruptions; explain confidentiality and its limits; no pressure; support
person offered; no leading questions; specific not vague; objective. Written
statements use the Incident Witness Statement Form (MPR-INT-0214 Appendix D).
See `interview-guide.md` for the question sets. Produce `witness-statement`
artefacts (one per witness).

### Stage 4 — Timeline and 5-Whys

Build the chronological event sequence from initiating events to the
situation being under control: actor, action or condition, time, evidence
reference. Sequence acts and states together. Mark points where the outcome
could have been interrupted — these are candidate absent or failed defences.
Run the 5-Whys chain from the event to the basic cause (the mechanism of
failure). Charts are rendered by `render_charts.py` (timeline, 5-whys). Flag
source conflicts as open questions.

### Stage 5 — Contributing factor analysis (Appendix C)

Work the four categories sharp-end to latent: Absent/Failed Defences (DF),
Individual/Team Actions (IT), Task/Environmental Conditions (WF+HF),
Organisational Factors (OR). See `taxonomy.md` for codes, check questions and
rating scales. For every Individual/Team Action keep asking "why did that make
sense at the time?" until you reach conditions and then organisational
factors. Nudge downward if only DF/IT factors appear. Test necessity: if
removing the factor would not have changed the outcome, park it as context.
The completed analysis goes into report Section 5.2 and the
`appendixc-worksheet` artefact; the PEEPO classification of contributing
factors goes onto the PEEPO chart.

### Stage 6 — Recommendations and Corrective Action Plan

Every contributing factor is addressed by at least one recommendation unless
the user documents why not. Apply the hierarchy of controls (elimination /
substitution / engineering above administrative above PPE); challenge
"retrain and remind" answers. The lead investigator reviews recommendations
with the Executive Leader and other leaders; workers may be consulted. CAP
fields: recommendation, responsible department, responsible person, date due —
entered into SAI360 and managed per MPR-INT-0049. Produce
`corrective-action-plan` artefact.

### Stage 7 — Report generation and approval

Fill the controlled WHS-TMP-0207 template with `build_report.py` (see
`template-map.md`). Required content (MPR-INT-0214 s4.6): factual recount,
injuries/treatment/prognosis, plant details (make, model, serial), witnesses
and statements, all contributing and causal factors, immediate actions already
implemented, further recommendations, agreed CAP with timeframes and
responsible persons, sign-off. Submit for closure approval per the Appendix A
approval path; record any conditions or rejected recommendations in the
approval conditions box. After approval: upload to SAI360 and ECM; findings
communicated by the Health and Safety Team.

## Cross-cutting disciplines

- **LPP:** all drafts marked "Privileged and Confidential – prepared solely
  for the purposes of obtaining legal advice"; distribution limited to the
  Investigation Table recipients; nothing external without Corporate Counsel
  clearance; photos marked to Corporate Counsel's attention and stored in the
  privileged folder.
- **Notifiable incidents:** site must not be disturbed except for prescribed
  reasons (assist injured, remove deceased, make safe, police investigation,
  Inspector permission) until an Inspector arrives or WHSQ confirms
  non-attendance. Notification is the H&S Manager / Environmental Scientist's
  role — confirm, never assert.
- **Psychosocial events:** trauma-informed; safe private interview settings;
  clear confidentiality limits; avoid re-traumatisation; separate the safety
  investigation from any disciplinary or performance action; led jointly by
  HR and H&S.
- **No fabrication:** record unknowns as data gaps or open questions and park
  them in Assumptions and Exclusions (report 3.1) until resolved.
