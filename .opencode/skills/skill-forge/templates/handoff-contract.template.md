# handoff-contract.template.md
# One file per build task: copilot/handoffs/<task-id>.md
# This file is BOTH the coordination record and the delegated-task text that can
# be pasted into Studio when the work crosses into child/connected agents.

# Handoff contract — __TASK_ID__

| Field | Value |
| ----- | ----- |
| Requester | __WHO_NEEDS_IT__ |
| Executor | __AGENT_OR_PERSON__ |
| Reviewer (QA gate) | __SUBAGENT_NAME__ |
| Created | __YYYY-MM-DD__ |
| Status | open → in-progress → delivered → verified |

## Inputs

| Input | Where | Notes |
| ----- | ----- | ----- |
| __E.g. template file__ | SharePoint link (downloaded to assets/templates) | sync date __DATE__ |
| __Data / decisions__ | __SOURCE__ | scope boundary: __WHERE_EXECUTOR_MUST_STOP__ |

## Deliverables

| Path | Description | Version |
| ---- | ----------- | ------- |
| .opencode/skills/__SKILL_ID__/ | skill package | v0.1.0 |
| copilot/uploads/__SKILL_ID__-v0.1.0.zip | upload artefact | — |

## Acceptance checklist

- [ ] `validate-package.py` passes with no FAIL (WARNs explicitly judged)
- [ ] SKILL.md description triggers test prompts worded like real user asks
- [ ] Scripts: allowed extensions, no network/package installs, positional args
- [ ] Instructions (if any) pass the 9-practice checklist
- [ ] No secrets / tenant URLs / personal data embedded
- [ ] Registry rows updated with validation result

## Validation log

```
__COMMAND__ __RESULT__ __DATE__
```

## QA findings (findings-only return)

- —

## Hand-back

- __WHAT_THE_REVIEWER_OR_USER_SEES_AND_WHAT_THEY_DECIDE_NEXT__
