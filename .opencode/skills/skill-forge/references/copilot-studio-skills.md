# Copilot Studio skills — platform rules (verified Nov 2026)

Sources: learn.microsoft.com/microsoft-copilot-studio/agents-experience/skills-overview ·
/microsoft-copilot-studio/guidance/multi-agent-patterns ·
/microsoft-365/copilot/extensibility/declarative-agent-skills ·
agentskills.io specification. Re-verify before quoting limits in deliverables.

## Skills in Copilot Studio

Agent Skills (agentskills.io) are portable packages of instructions, scripts and
resources. The orchestration runtime activates a skill when the user's request
matches its description. Two Studio harnesses:

| Harness | Skill model | Create/upload |
| ------- | ----------- | ------------- |
| **GitHub Copilot harness** (agents-experience) | name + description + Markdown instructions; upload a skill file or **package**; supports agentskills.io packages | Build tab → Add skill: upload existing, create from blank, generate with AI |
| **Standard harness** (Customer Conversation) | **Generative** skills (same Markdown model) and **Topic** skills (deterministic authored flows) | Add skill dialog → Generative or Topic |

Built-in document-analysis skills already cover `.csv .docx .html .md .pdf
.pptx .xlsx` analysis (they read/summarise; they do not *create* documents).
For file/data operations, Studio provides run-time packages; our skills ship
their own deterministic scripts.

## Package format (open Agent Skills standard)

```
<skill-id>/               # id = directory name, kebab-case
├── SKILL.md              # required: frontmatter + Markdown instructions
├── scripts/              # executable code (positional CLI args)
├── references/           # policy/reference content loaded on demand
└── assets/               # templates, static resources
```

Frontmatter fields

| Field | Rule |
| ----- | ---- |
| `name` | required; lowercase kebab-case, ≤64 chars; **must equal directory name** |
| `description` | required; ≤1024 chars; what it does + trigger keywords |
| `license` | optional |
| `compatibility` | optional; ≤500 chars; runtime/product expectations |
| `metadata` | optional key-value map (author, version, surfaces) |
| `allowed-tools` | optional space-delimited list (experimental) |

Progressive disclosure: advertise (~100 tokens) → load body (<5k tokens
recommended; M365 sandbox guidance caps skill instructions at 20,000 chars)
→ read resources → run scripts. Body <500 lines.

## Limits (as documented Nov 2026)

| Item | Agent Builder (M365) / declarative | Agents Toolkit / Studio dir upload |
| ---- | ---------------------------------- | ----------------------------------- |
| Skills per agent | 8 skills max — Treat 8 as the ceiling for any delivery | 8 |
| Skill package | `.zip` ≤50 MB | directory; app package ≤10 MB |
| Max file size | 25 MB | — |
| Files per package | 350 across all skills | 350 |
| Dir depth | 3 | 3 |
| Reuse across agents | not supported | not supported |

Declarative agents (secondary surface): instructions ≤8,000 chars; reference
skills **at high level only**; never store instructions in SharePoint.

## Script sandbox (hard constraints)

- **No network** at runtime. No package installs. Stdlib-only `.py` scripts are
  the reliable choice, or pre-existing packages only.
- Allowed script types: `.py`, `.js`, `.mjs`, `.cjs`, `.ts`, `.mts`, `.sh`, `.bash`.
  `.ps1/.cmd/.bat/.exe/.dll` **fail** — a `.ps1` habit from Windows orgs is a
  common packaging mistake.
- Scripts receive args as a JSON array of positional strings.
- Sensitivity labels on skill files are retained and honored; connectors/API
  plugins are invoked by the *agent* (orchestrator), never from sandbox scripts.

## Governance & coordination touchpoints

- Admins can enable/disable agent features per tenant; Purview Information
  Barriers tenants: end users cannot add skills to self-made agents.
- Skills are reusable across Studio agents from the Build tab; the registry
  (`copilot/registry.md`) tracks which agents reference which skills.
- Connected/child agents carry their own governance: parent delegation must
  never be a way around a parent restriction (see instructions-authoring.md §9).
