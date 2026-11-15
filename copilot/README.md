# Copilot agent workspace

## Command centre

- **Primary agent to achieve this** — switch the session to
  `copilot-skill-forge` (or invoke it as a subagent: "use copilot-skill-forge
  to build …"). Its standards and templates live in the `skill-forge` skill.
- **Ready-to-use skill** — `org-document-suite` fills the organisation's Word
  / PowerPoint / Excel templates from `data.json`.

## Layout

| Path | Role |
| ---- | ---- |
| `.opencode/agents/copilot-skill-forge.md` | dedicated builder agent (Copilot skills, scripts, sub-agent instructions) |
| `.opencode/skills/skill-forge/` | the builder's standards: platform rules, instruction authoring, doc-generation conventions, coordination, templates, `validate-package.py` |
| `.opencode/skills/org-document-suite/` | complete template-document skill (`fill-template.py` — stdlib only, sandbox-safe) |
| `copilot/registry.md` | catalogue, owners, statuses, handoff index |
| `copilot/handoffs/` | one contract per build task (created by the forge) |
| `copilot/uploads/` | validated zips ready for Studio / Agent Builder upload |

## Quickstart without templates

```
py -3 .opencode/skills/org-document-suite/scripts/fill-template.py <template.docx> data.json out.docx --audit
py -3 .opencode/skills/skill-forge/scripts/validate-package.py .opencode/skills/org-document-suite
```

Once the SharePoint template links arrive, drop copies into
`.opencode/skills/org-document-suite/assets/templates/` and register them —
the forge takes over from there.
