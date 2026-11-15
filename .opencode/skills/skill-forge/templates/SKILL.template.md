# SKILL.template.md — copy into `<skill-id>/SKILL.md`
# Replace __TOKEN__ placeholders, then delete this header block.
# Rules: name = directory name, kebab-case. Description says WHAT + WHEN (≤1024 chars).
---
name: __SKILL_ID__
description: __WHAT_THE_SKILL_DOES_AND_WHEN_TO_USE_IT — keep trigger keywords users would actually say__
license: internal-use
compatibility: __E.g._Requires python3 (or `py -3` on Windows). Stdlib only; no network needed.__
metadata:
  author: __TEAM__
  version: "0.1.0"
  surfaces: __Copilot Studio (GitHub Copilot harness) and/or standard harness / Agent Builder__
---

# __SKILL_ID__

One-word purpose statement: what this skill produces.

## When to use

- Trigger 1 (a sentence a user would actually write).
- Trigger 2.

## Workflow

1. **Intake** — what the agent confirms before acting (inputs, permissions,
   output location). If anything is missing, ask — do not guess.
2. **Prepare** — read `references/__DATA_OR_POLICY__.md` for the data/policy
   contract. Never skip this step.
3. **Execute** — run the script(s):

```
python3 scripts/__SCRIPT__.py __POSITIONAL_ARGS__
```

4. **Verify** — expected exit code, how the agent checks the result, and what
   the report means. Exit-code table:
   `0 = success · 3 = recoverable data issue (retry after fixing input)`.
5. **Hand back** — final summary the agent gives the user: artefact paths,
   remaining actions, and any warnings lifted verbatim from the report.

## Files

| Path | Role |
| ---- | ---- |
| `scripts/__SCRIPT__` | __one-line purpose__ |
| `references/__REF__` | __one-line purpose__ |
| `assets/__ASSET__` | __one-line purpose__ |

## Guardrails

- Never __EDIT__ the template/source of truth; produce outputs only.
- No network calls, no package installs at runtime (sandbox constraint).
- No secrets, tenant URLs or personal data embedded in scripts or data files.
- On conflict between this skill and the platform template, stop and ask.
