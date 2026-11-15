---
name: skill-forge
description: Author, validate and coordinate complete Microsoft Copilot skill packages (SKILL.md + scripts + resources), document-generation scripts for organisation templates, and parent/child agent instruction sets for Copilot Studio. Load before building any Copilot skill, agent instruction set, or coordination artefact.
license: internal-use
compatibility: Targets Microsoft Copilot Studio agents (GitHub Copilot harness and standard harness); packages follow the agentskills.io open specification.
metadata:
  author: copilot-skill-forge
  version: "1.0.0"
---

# skill-forge — build Copilot skills and agent instructions

You produce **ready-to-upload artefacts** for Microsoft Copilot, not drafts:
complete skill packages, agent instructions and coordination records.

## Operating loop

1. **Intake.** Read `copilot/registry.md` (or the registry path given by the
   coordinator) first: what exists, who owns it, what is in flight. Then
   confirm with the user: target surface (Studio harness), audience, skill name
   (lowercase kebab-case, 1–64 chars), and templates/data the task needs.
2. **Author.**
   - New skill package → `templates/SKILL.template.md`, structured as
     `SKILL.md` + `scripts/` + `references/` + `assets/`.
   - Copy the `org-document-suite` pattern for anything that writes
     organisation-templated documents.
   - Parent agent instructions → `templates/parent-agent.instructions.template.md`
   - Child/connected agent instructions → `templates/child-agent.instructions.template.md`
3. **Validate** before anything leaves the workspace:
   ```
   python3 scripts/validate-package.py <skill-package-dir> [--zip copilot/uploads/<name>-v<N>.zip]
   ```
   Fix FAILs, judge WARNs explicitly. Platform rules in
   `references/copilot-studio-skills.md`.
4. **Coordinate.** Record a handoff via `templates/handoff-contract.template.md`,
   update the registry (`templates/registry.template.md` format), and spawn a
   QA subagent for independent review when the work is user-facing. Contract
   mechanics in `references/coordination.md`.
5. **Hand back** the delivery summary: artefact paths, validation result,
   registry status, and the user's next action (usually: upload the zip, or
   paste instructions into Studio).

## Standards (combine with references)

- **SKILL.md frontmatter is contract, not decoration** — `name` must equal the
  directory (kebab-case), `description` ≤1024 chars must say *what it does and
  when to use it*; body <500 lines, load cost <5k tokens. Detail goes into
  `references/`, not the body.
- **Scripts are deterministic.** Prefer a script over prose when a step must be
  repeatable. Stdlib-only Python is portable to the Copilot sandbox; scripts run
  **no network** there. Allowed script types: `.py .js .mjs .cjs .ts .mts .sh .bash`
  — never `.ps1/.cmd/.bat/.exe`.
- **Instructions use strong directive language** (MUST / ONLY / NEVER) and cite
  concrete tools; the 9 multi-agent practices apply whenever a parent delegates
  (`references/instructions-authoring.md`).
- **Never hard-code** tenant URLs, secrets or user-identifying data inside
  packages or instructions. SharePoint sources are recorded in a reference
  table, not fetched by scripts.

## Output layout

Skill packages live beside `SKILL.md` so agents load resources relative to it:

```
.opencode/skills/<skill-id>/        # source of truth, Agent Skills format
copilot/
├── registry.md                     # catalogue + owners + status
├── handoffs/<task-id>.md           # one open contract per build task
├── uploads/<skill-id>-<version>.zip
└── agents/<agent-name>/...         # instruction sets awaiting paste into Studio
```
