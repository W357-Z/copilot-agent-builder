# Writing instructions for Copilot agents and sub-agents

Grounded in learn.microsoft.com: declarative agent instructions guidance and
Copilot Studio multi-agent orchestration patterns. Templates:
`../templates/parent-agent.instructions.template.md`,
`../templates/child-agent.instructions.template.md`.

## Instruction components (declarative & Studio)

1. **Purpose** — the goal in one or two sentences.
2. **General guidelines** — tone, restrictions, response rules.
3. **Skills** — reference at a *high level* ("use the XXX skill"), never
   duplicating a skill's steps; skills live in the skill package.
4. Workflows (goal / action / transition), error handling, interaction
   examples, closing behaviour.

Limits: declarative agents ≤8,000 chars in the instruction field — move detail
into skills. Studio standard harness: keep equally lean; check the current
field cap in the tenant UI before finalising.

## Style rules (strict)

- Directive language: MUST / ONLY / NEVER / DO NOT. Soft phrasing loses
  conflicts with system-level instructions.
- Atomic tasks: one action per step; "extract metrics" and "summarise findings"
  are two steps, not one.
- Sections (`##`) group parallel content; numbered steps only for true
  sequences; bullets for independent tasks. Clean Markdown — broken lists cause
  merged steps at runtime.
- Specify tone, verbosity and an **output contract**: format, detail cap,
  include/exclude lists, plus a final self-evaluation step.
- Define org vocabulary and acronyms; add few-shot examples for complex flows.
- **Never** store instructions in a SharePoint/knowledge source to dodge limits —
  that content is sanitised by prompt-injection classifiers and can be edited by
  anyone with write access.

## The 9 multi-agent practices (standard harness; apply the intent in any
multi-agent setup)

| # | Practice |
| - | -------- |
| 1 | Single response principle: parent is the only agent that talks to the user |
| 2 | Every subagent's instructions declare their role ("you are a subagent; do NOT reply to the user") |
| 3 | Strong directive language throughout |
| 4 | One, non-overlapping knowledge source per subagent (overlapping sources = duplicate work) |
| 5 | Distinct, accurate descriptions for each subagent — the parent routes on them |
| 6 | Parent instructions define the full pattern: invoke → wait → combine → respond |
| 7 | Delegated tasks repeat "Return findings only. Don't reply to the user." |
| 8 | Test with domain-mismatch queries (outside every child's domain) |
| 9 | Ask when a follow-up is expected; inform only for one-way messages |

Quick checklist to run before delivering any subagent instruction set:
parent-owns-response ✔ subagent-role-declared ✔ strong-language ✔
unique-knowledge ✔ distinct-descriptions ✔ orchestration-pattern ✔
delegation-reminder ✔ domain-mismatch-tests ✔ ask-vs-inform ✔

## Inline vs connected vs child agents

- **Inline agents** (topics/subroutines inside one agent): share context, keep
  focused, cheap. Default choice.
- **Connected agents** (separate agents the parent calls): only when the
  subtask has its own tools/knowledge domain, different governance, or reuse
  across multiple mains. Check each connected agent's context-inclusion
  setting — history is not guaranteed to flow. Treat the connected agent as a
  described tool from the parent's perspective.
- **Child agents** always receive parent context — still declare their role
  explicitly.

## Test plan minimum

1. Domain-mismatch query (must return a graceful "nothing found" from children).
2. Each conversation starter.
3. One query that should trigger each attached skill.
4. One escalation/failure path.
5. Two-session check that only one agent answered per turn.

Record results in the delivery's handoff contract. For iterative tuning note
`special_instructions.discourage_model_knowledge: true` (manifest) when answers
must ground only on org knowledge, and Work IQ Dev Tools for evaluations.
