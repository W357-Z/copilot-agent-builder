# Contributory factors taxonomy (MPR-INT-0214 Appendix C)

Codes transcribed from MPR-INT-0214 v3 Appendix C (Analysis of Contributory
Factors). Verify against the currently controlled issue before quoting in a
final report. Reasons are mandatory for every ticked code — the taxonomy
requires reasons, not just ticks.

## Category order (sharp end to latent causes)

1. **Absent / Failed Defences (DF)** — rating: Absent / Some failure /
   Complete failure.
   Check question: does the item describe the equipment, work process,
   control measure, detection system, procedure or attribute which normally
   prevents this event or limits the consequences?
2. **Individual / Team Actions (IT)** — rating: Absent / Inadequate /
   Unsuitable (code-specific variants below).
   Check question: does the item tell you about an error or violation of a
   standard or procedure made in the presence of a hazard?
3. **Task / Environmental Conditions (WF + HF)** — rating: Some /
   Significant.
   Check question: does this item describe task demands, work environment,
   individual capabilities or human factors that promoted errors / violations
   or undermined the effectiveness of the system's defences?
4. **Organisational Factors (OR)** — rating: Contributing.
   Check question: does this item identify a standard organisational factor
   present before the event which resulted in the task / environmental
   conditions, or allowed them to go unaddressed?

## DF — Absent / Failed Defences

| Code | Factor |
| ---- | ------ |
| DF1 | Detection systems / procedures |
| DF2 | Protection systems / procedures |
| DF3 | Warning systems / procedures |
| DF4 | Guards or barriers |
| DF5 | Recovery systems / procedures |
| DF6 | Escape systems / procedures |
| DF7 | Rescue systems / procedures |
| DF8 | PPE |
| DF9 | Hazard identification |
| DF10 | Risk management |
| DF11 | Safe work procedure |
| DF12 | Supervision |
| DF13 | Other (specify) |
| DF14 | Other (specify) |

## IT — Individual / Team Actions

| Code | Factor | Rating variants |
| ---- | ------ | --------------- |
| IT1 | Supervision | Absent / Inadequate / Unsuitable |
| IT2 | Authority | Absent / Inadequate / Unsuitable |
| IT3 | Operating speed | Absent / Inadequate / Unsuitable |
| IT4 | Equipment use | Absent / Exceeded limits / Misuse / Unsuitable selection |
| IT5 | PPE | Absent / Exceeded limits / Misuse / Unsuitable selection |
| IT6 | Work procedure followed | Partially / Not followed / Unsuitable |
| IT7 | Change management | Absent / Inadequate / Unsuitable |
| IT8 | Equipment / material handling | Absent / Inadequate / Unsuitable |
| IT9 | Horseplay | Absent / Inadequate / Unsuitable |
| IT10 | Hazard recognition | Absent / Inadequate / Unsuitable |
| IT11 | Hazard management | Absent / Inadequate / Unsuitable |
| IT12 | Work method | Absent / Inadequate / Unsuitable |
| IT13 | Occupational hygiene practices | Absent / Inadequate / Unsuitable |
| IT14 | Other (specify) | Absent / Inadequate / Unsuitable |

## WF — Workplace factors (Task / Environmental Conditions)

| Code | Factor |
| ---- | ------ |
| WF1 | Lighting |
| WF2 | Weather |
| WF3 | Gas / dust / fumes / contaminants |
| WF4 | Noise |
| WF5 | Wildlife |
| WF6 | Surface gradient / conditions |
| WF7 | Workspace access / restriction |
| WF8 | Housekeeping |
| WF9 | Tools / equipment condition / availability |
| WF10 | Task planning / preparation |
| WF11 | Routine / non-routine task |
| WF12 | Abnormal operational situation / condition |
| WF13 | Risk perception / management |
| WF14 | Work procedures |
| WF15 | Permit to Work |
| WF16 | Chemical |
| WF17 | Ventilation |
| WF18 | Material availability and suitability |
| WF19 | Fire and / or explosion |
| WF20 | Congestion / restriction / access |
| WF21 | Equipment integrity |
| WF22 | Radiation |
| WF23 | Other (specify) |

## HF — Human factors (Task / Environmental Conditions)

| Code | Factor |
| ---- | ------ |
| HF1 | Complacency / motivation |
| HF2 | Drugs / alcohol |
| HF3 | Familiarity with task |
| HF4 | Fatigue |
| HF5 | Time pressure |
| HF6 | Peer pressure |
| HF7 | Physical capabilities |
| HF8 | Mental capabilities |
| HF9 | Physical stress |
| HF10 | Mental stress |
| HF11 | Confidence level |
| HF12 | Secondary goals / external factors |
| HF13 | Personal issues |
| HF14 | Distraction / pre-occupation |
| HF15 | Experience / knowledge / skill for task |
| HF16 | Competency |
| HF17 | Behavioural beliefs |
| HF18 | Personality / attitude |
| HF19 | Poor communication |
| HF20 | Poor shift patterns / overtime working |
| HF21 | Situational awareness |
| HF22 | Passive tolerance of violations |
| HF23 | Perceived licence to operate |

## OR — Organisational Factors

| Code | Factor | Code | Factor |
| ---- | ------ | ---- | ------ |
| HW | Hardware | MM | Maintenance Management |
| TR | Training | DE | Design |
| OR | Organisation | RM | Risk Management |
| CO | Communications | MC | Management of Change |
| IG | Incompatible goals | CM | Contractor Management |
| PR | Procedures | OC | Organisational Culture |
| MS | Management Systems | RI | Regulatory Influence |
| SU | Supervision | OL | Organisational Learning |
| VM | Vehicle Management | | |

## Error and violation classification (Stage 4 sharpening)

Classify each Individual / Team Action:

| Type | Meaning | Typically points to |
| ---- | ------- | ------------------- |
| Slip | right intention, wrong execution | design and defences (DF) |
| Lapse | memory failure, missed step | design and defences (DF) |
| Mistake | right execution of the wrong plan | planning, competency (TR, WF10, HF16) |
| Routine violation | the normal way the job is done | procedure-vs-reality mismatch (PR, MS) |
| Situational violation | forced by the day's circumstances | planning and resourcing (IG, OR) |
| Exceptional violation | rare, deliberate departure | culture, supervision (OC, SU) |

## Data mapping

Each confirmed factor becomes an entry in the data contract's
`factors.<category>` list (see `data-contract.md`): `code` (from this
taxonomy), `text` (what happened, in fact-finding language), `rating`
(category scale), `reason` (why it contributed — evidence-linked). The ICAM
chart and the Appendix C worksheet are generated from this structure.
