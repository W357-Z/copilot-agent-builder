# Coordination — registry, handoff contracts, QA gates

Deliverables are grouped into *contracts*, not loose chats. This reference
defines the three artefacts and the loop between them.

## 1. Registry (`copilot/registry.md`)

The single source of truth for what exists. Every artefact row:

| Artifact ID | Type | Path | Surfaces | Owner | Status | Last validated |
| ----------- | ---- | ---- | -------- | ----- | ------ | -------------- |

- **Artifact ID**: kebab-case, unique (`skill-report-suite`, `agent-pmo-parent`).
- **Type**: `skill` | `agent-instructions` | `coordination`.
- **Surfaces**: Studio harness(s) + any secondary target (Agent Builder, local).
- **Status**: `draft` → `validated` → `published` (uploaded to tenant) →
  `deprecated`.
- **Rules**: registry rows are only added/updated inside a handoff contract
  with validation output; never mark `published` until the user confirms upload;
  entry must record *who* owns maintenance.

## 2. Handoff contracts (`copilot/handoffs/<task-id>.md`)

One file per build task, containing:

- IDs: task, requester, executor, reviewer.
- Inputs (paths/URLs/decisions) and Deliverables (paths).
- Acceptance checklist (concrete, checkable).
- Validation commands + captured output (validate-package exits, fill exit
  codes, test-plan results).
- Status: `open → in-progress → delivered → verified`.

**Queued vs parallel work.** Executors must not edit artefacts listed in an
`open`/`in-progress` contract owned by someone else. Parallel-friendly tasks
are declared "parallel-safe" with a scope list; conflicts re-serialize.

## 3. QA gate

For user-facing deliverables spawn an independent review subagent (in OpenCode:
`subagent` tool, `general/explore` agent, or a dedicated `qa` agent if the
registry lists one):

- Prompt contains: the handoff contract ID, artefact path, the checklist to
  verify, and "return findings only, do not contact the user".
- QA verifies: package validates clean; SKILL.md description would trigger for
  plausible user requests; instructions follow the 9-practice checklist;
  no secrets/tenant URLs embedded; scripts have allowed extensions and no
  network calls.
- Findings go back into the contract; executor fixes and re-validates;
  handback only when the gate passes.

## Agent mapping

| Setting | Claude/Copilot equivalents |
| ------- | -------------------------- |
| Parent = single response owner | parent orchestrator agent |
| Subagent instructions = role-declared, findings-only | connected/child agent briefs |
| Registry = agent catalogue | Studio agent list, Agents Toolkit manifests |
| Handoff contract = delegated task text | parent→child task payloads |

The same contract file both records the build and doubles as the **task text
pasted into Studio** when delegating between Copilot agents — write it so each
side can execute it without extra context.

## Failure & escalation

- Blocked intake (missing templates/access): reopen contract status `open`,
  mark needs-input, notify requester — never fabricate inputs.
- Platform change suspicion (limits, harness behaviour): re-verify Learn docs
  and record the check date in the contract before overriding this reference.
- Registry drift (artefact changed outside a contract): flag at next QA gate,
  reconcile row, note the correction in the contract.
