# Copilot artefact registry

Maintained by the `copilot-skill-forge` agent. Updated only inside a handoff
contract with validation output attached — see
`.opencode/skills/skill-forge/references/coordination.md`.

## Catalogue

| Artifact ID | Type | Path | Surfaces | Owner | Status | Last validated |
| ----------- | ---- | ---- | -------- | ----- | ------ | -------------- |
| skill-forge | skill | `.opencode/skills/skill-forge` | Studio (both harnesses), Agent Builder, local agents | forge team | validated — `validate-package.py` PASS (2026-11-08) | 2026-11-08 |
| org-document-suite | skill | `.opencode/skills/org-document-suite` | Studio (GitHub Copilot harness), Agent Builder, local agents | forge team | validated — fill smoke-tested (docx/pptx/xlsx/audit); zip staged at `copilot/uploads/org-document-suite-v0.1.0.zip` | 2026-11-08 |
| gawb-icam-investigation | skill | `.opencode/skills/gawb-icam-investigation` | Studio (GitHub Copilot harness + standard harness) | forge team (for GAWB H&S) | validated — `validate-package.py` PASS, 1 judged WARN (.dotx by design); report verified over all 16 rendered pages (fill audit 39/39, missing=[]); 5 artefact builds exit 0; QA gate all-PASS, findings folded in; zip staged at `copilot/uploads/gawb-icam-investigation-v0.1.0.zip` (contract H-2026-11-15-icam-suite) | 2026-11-15 |

## Agents in flight

| Agent ID | Harness | Instruction artefact | Skills attached | Children | Status |
| -------- | ------- | -------------------- | --------------- | -------- | ------ |
| copilot-skill-forge | local builder agent (OpenCode) | `.opencode/agents/copilot-skill-forge.md` | skill-forge, org-document-suite | — | active |
| gawb-icam (Studio parent, to be created by user) | Copilot Studio | `copilot/agents/gawb-icam/parent.instructions.md` (paste block ≈7.1k chars) | gawb-icam-investigation | optional document-builder child | validated — 9-practice checklist + test-plan minimum recorded in contract H-2026-11-15-icam-suite; awaiting tenant upload |

## Notes

- Pending intake: SharePoint/OneDrive links for the organisation's `.docx`,
  `.pptx`, `.xlsx` templates → owner downloads into
  `.opencode/skills/org-document-suite/assets/templates/`, records them in
  `references/data-contract.md`, then flips the status to `draft — awaiting
  org tokens` until the template owners confirm the `{{Token}}` inventory.
