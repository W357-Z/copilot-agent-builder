# Interview guide (MPR-INT-0214 s4.3.4 + GAWB Guidelines for Conducting Interviews)

Question sets for planning, running and closing witness interviews. Sources:
MPR-INT-0214 Incident Investigation Procedure v3 s4.3.4 and the GAWB
"Guidelines for Conducting Interviews" (2-page practice guide). Verify against
the currently controlled issues before quoting requirements in a report.

## Who to interview (s4.3.4)

- People present at the time of the incident.
- People involved with the initial response.
- People responsible for operating, maintaining and managing the relevant
  machinery, processes or projects.

Statements are **verbal accounts, not facts** — validate every material claim
against photos, records and physical conditions before it enters the analysis.

## Mandatory conditions (s4.3.4 — check all before every interview)

- Private location, free of interruptions.
- Confidentiality of personal information maintained; **limits to
  confidentiality explained** up front (e.g. notifiable incidents, unlawful
  conduct allegations, psychosocial disclosures may have to be escalated).
- Interviewee is not pressured into providing a statement or information.
- Interviewee is informed they may have a support person present.
- No leading questions, no prompting for answers.
- Objectivity maintained; no interruptions or takeovers between team members.
- Vague generalisations avoided — keep the account specific to what the
  witness personally saw, heard and did.

Recording: notes or recording only **with prior permission**. If the witness
objects to recording, ask why; if they still object, offer to let them review
the typed notes instead.

## The welcome (opening script)

1. Welcome the witness; introduce all parties present and their roles.
2. State the purpose of the interview.
3. Emphasise: the team is finding ways to prevent a recurrence, **not
   apportioning blame**; every attempt will be made to keep identities
   confidential.
4. Stress the team is impartial and unbiased.
5. Explain note-taking / recording (with prior permission) and the accuracy
   purpose; offer the review-the-notes option if the witness objects.
6. Record the facts: name, employer, work location, job classification, and
   their involvement in the activity at the time of the incident.

## Question set A — incident sequence

Open broad, then drill:

- "In your own words, tell us what happened in this incident?"
- Then short, simple clarification questions on anything unclear.

Sequence questions (drill until you can build the timeline):

- What were you doing immediately before the event?
- What did you see / hear / notice first?
- What happened next, step by step, and at what times?
- Who else was present, and what did they do?
- What did you do immediately after, and what did others do?
- What changed in the scene between the event and when you left it?

## Question set B — how the activity was planned and conducted

Planning and risk assessment:

- Was a job safety analysis conducted while planning the activity?
- Were hazards identified and risks evaluated?
- Was the Health, Safety and Environment Department contacted for
  assistance? Was the response adequate?
- Did you have any concerns prior to the incident, and did you discuss them
  with your supervisor or the HSE Department?
- Why did activity planning not anticipate and control the conditions that
  caused the incident?

Hardware, design and maintenance:

- Was the correct hardware available?
- Was the hardware (facilities and equipment) adequately designed? Was the
  design reviewed?
- Was the equipment properly obtained and installed? Tested before use?
- Was there a functioning inspection and maintenance plan?
- Were pertinent codes and standards available, and incorporated into the
  control plan?

People and competence:

- Were personnel adequately selected and trained for this activity? Were
  provisions made for training and upgrading the skills of new personnel?
- Was the possibility of worker performance errors provided for when the
  activity was planned?

Environment and controls:

- If abnormal environmental factors (wind, rain, ice, heat, humidity, noise,
  lighting, high altitude, time) were significant, were adequate
  countermeasures planned and taken?
- Was a reasonable combination of physical barriers and behavioural controls
  selected? Were the controls and barriers in place and working?
- Were any special emergency controls required, and were they working?
- If a safe work procedure was required, was it available and functioning?
- Were job instructions prepared and followed?

Supervision and correction:

- Did the supervisor observe the activity in progress, and were they
  satisfied with the conduct of operations?
- If the supervisor noticed changes in work practices, did they react
  correctly?
- If supervisors or fellow workers observed performance errors, were
  good-faith efforts made to correct them?
- If drugs, alcohol, family problems or emotional disturbances contributed to
  a performance error, were efforts made to solve those problems before the
  incident?

Emergency response and history:

- If some action could have been taken at the onset of the incident to reduce
  its impact, was it taken?
- Did operating personnel and others in the vicinity respond properly?
- Was the site emergency response plan followed?
- Did emergency response personnel respond, follow their plan and perform
  effectively?
- If a similar incident occurred before, was adequate remedial action taken?
- Were management support services and upper management's safety commitment
  evident prior to this incident?
- Did management take reasonable measures to prevent this incident?

## Question set C — ICAM probing (beyond the GAWB guide)

Use after the account is established, to reach latent factors. Never leading —
offer options, don't imply the answer:

- "What made that the sensible thing to do at the time?" (local rationality)
- "What made it hard to do the right thing that day?" (task/environment)
- "Has this happened before, or nearly happened?" (history, tolerance)
- "What would have stopped this earlier?" (absent/failed defences)
- "Who else would normally have known or checked this?" (organisation)
- "What usually happens around here when procedure and the job disagree?"
  (work-as-done vs work-as-prescribed)

Map every answer into PEEPO columns and, later, Appendix C codes — a fact
that fits no code is either context or a data gap.

## The closing

- Thank the witness for their time and account.
- Explain that another interview may be necessary if additional information
  is needed.
- Encourage the witness to contact the team if they think of additional
  information that may help the investigation.
- Confirm how they can review their statement (Appendix D form) and what
  happens next with the information they gave.

## Written statements (MPR-INT-0214 Appendix D)

Capture statements on the Incident Witness Statement Form. Fields the
`witness` artefact covers: full name, position/role, employer, normal work
location, contact details, date/time and location of the incident, account of
what was witnessed (first person), and signature/date lines. The skill's
`build_doc.py witness` output reproduces this structure for wet signature.

## Psychosocial-sensitive interviews

For psychosocial incidents or significant psychosocial impact (per
MPR-INT-0102 / MPL-INT-0318 escalation): trauma-informed approach; private
safe setting; clear confidentiality limits stated before the account; avoid
re-traumatisation (no repeated re-telling beyond need); affected workers
offered support (EAP, critical-incident response); the safety investigation
stays separate from any disciplinary or performance process; interviews led
jointly with HR and H&S.
