# SIH26165: specification-driven development pack

Prepared for Harshit and the SIH team. Version 1.0 · 3 September 2026.

**Deliverable status:** planning documents only. No application, labeled dataset, trained model, evaluation result or deployment is included. All task checkboxes start incomplete. The small examples are synthetic teaching fixtures.

## Recommended approach

Build a working report-review application while developing a compact, fine-tuned NLP engine. Train **microsoft/deberta-v3-small** for SIF classification first, then add a multi-label Life-Saving Rule head. Train a **Qwen/Qwen2.5-1.5B-Instruct QLoRA adapter** as a separate, bounded learning experiment. Compare each model with baselines before choosing the deployed engine.

The compact classifier is a transformer-based NLP model. It is valid to describe a completed, evaluated implementation as a fine-tuned NLP engine. Describe a QLoRA experiment as LLM fine-tuning only after an adapter was actually trained, saved, reloaded and evaluated. Neither description implies safety certification.

This changes the earlier Next.js-only recommendation: use **Next.js/TypeScript + FastAPI/Python + Supabase Postgres** so your own trained weights can run behind the same API as the initial hosted-model baseline. Use one application workflow, not an autonomous multi-agent system inside the product.

## What to read

| File | Purpose |
|---|---|
| [PRD.md](PRD.md) | Product goal, scope and definition of done |
| [AGENTS.md](AGENTS.md) | Coding-agent instructions and evidence rules |
| [SPECS.md](SPECS.md) | Authoritative behavior, API and data contracts |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, model adapters and durable job handling |
| [TASKS.md](TASKS.md) | Dependency-ordered implementation tasks |
| [DATA_PLAN.md](DATA_PLAN.md) | Turn the sourcebook into an eligible dataset |
| [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md) | SIF and rule-label definitions |
| [FINE_TUNING_GUIDE.md](FINE_TUNING_GUIDE.md) | Beginner path through classifier training and QLoRA |
| [EVALUATION.md](EVALUATION.md) | Leakage controls, metrics and promotion gates |
| [TEST_PLAN.md](TEST_PLAN.md) | Behavior and deployment acceptance checks |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Hosting, release, rollback and cost planning |
| [SECURITY.md](SECURITY.md) | Data access, credentials and model-input boundaries |
| [PROMPTS.md](PROMPTS.md) | Copy-ready agent and application prompts |
| [DECISIONS.md](DECISIONS.md) | Why this plan differs from the first proposal |
| [STATUS.md](STATUS.md) | Honest implementation and experiment state |
| [DEMO_AND_PITCH.md](DEMO_AND_PITCH.md) | Demo script and six-slide evidence plan |
| [REFERENCES.md](REFERENCES.md) | Sourcebook mapping and current technical references |

Read this file, PRD, AGENTS, SPECS and TASKS first. Open the specialist documents when their tasks begin.

## Start with an agent

1. Create an empty project repository, or inspect the existing project before changing it.
2. Copy these Markdown files into the repository root. Keep this pack's documents together so relative links work.
3. Give your coding agent the kickoff prompt in PROMPTS. Agents that do not automatically read AGENTS.md must be instructed to read it.
4. Implement the first end-to-end slice before adding features: authenticated demo session → submitted report → actual model call → saved result → reopened result.
5. Run meaningful checks, record evidence in STATUS and continue through the ready tasks. Do not restart the entire specification process for each feature.
6. In parallel with product work, the human team collects and reviews data. The agent may prepare parsers and draft labels; human-reviewed labels remain distinct.
7. Train in Colab, export the resulting artifacts, and have the agent integrate the selected model behind the existing API.

Spec-driven development is the loop **requirement → bounded task → implementation → observable check → recorded evidence**. The files improve consistency; they do not guarantee that generated code is correct. The workflow follows the general staged approach documented by GitHub Spec Kit [REF01], without requiring that tool to be installed.

## Milestones

- **M0 / project and contracts:** data fields, labels, API and honest sample mode are defined.
- **M1 / real-inference flow:** a fresh report goes through actual inference and persists.
- **M2 / review and dashboard:** corrections, batches, exports and reconciled charts work.
- **M3 / data and own NLP:** reviewed splits, trained encoder, evaluation and model deployment exist.
- **M4 / QLoRA experiment:** saved adapter, base-vs-tuned comparison and serving decision.
- **M5 / completion audit:** claimed requirements match recorded evidence.

Plan approximately 10 days for the product workflow and deployment and 2–3 weeks for a reviewed-data/training iteration, depending mainly on source access and reviewer time. These are planning estimates, not promises. If the deadline is shorter, preserve the functional demo and describe training progress accurately.

## Human work you cannot delegate away

Harshit owns scope, accounts, budget and final claims. A teammate or safety mentor must review label definitions, difficult labels and the interpretation of false negatives. If no qualified safety reviewer is available, say “team-annotated pilot data,” not “expert-validated data.”

No cloud spend is authorized by this pack. Prepare local work and deployment settings first; use any budget already authorized in the working session. Confirm a new paid commitment only when a concrete costed action is ready.

## Source basis

The supplied sourcebook contains 30 source entries and 48 hyperlinks. It is a catalogue, not a ready-to-train dataset. Both attached copies are byte-identical. Its source IDs S01–S30 are retained in DATA_PLAN and REFERENCES. The original file has SHA-256:

2eb8a34efa504b0fadf5ce6e8999664a0026f2a77275d6c169633f9f0bd9c64c

Model cards, training documentation and hosting restrictions were checked on 3 September 2026. See REFERENCES for links; recheck mutable prices and access before spending.
