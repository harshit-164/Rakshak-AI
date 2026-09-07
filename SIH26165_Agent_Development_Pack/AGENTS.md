# Instructions for implementation agents

These instructions apply when this pack is used to build the SIH26165 project. The current delivered pack is a plan, not an instruction to start implementation during a planning-only request.

## Goal and authority

Deliver the workflows and observable behavior in PRD.md and SPECS.md. Read README.md, SPECS.md, TASKS.md and STATUS.md before starting. Consult ARCHITECTURE.md and the relevant specialist file for the selected task.

Follow the live user's instructions and the environment's higher-priority instructions. Within the project, SPECS owns field names, state transitions, API behavior and constants; PRD owns scope; ANNOTATION_GUIDE owns label meaning; EVALUATION owns experiment interpretation. If these disagree, resolve the inconsistency explicitly and update affected documents before coding against the changed contract.

Routine implementation details are yours to choose. Document assumptions. Ask only when a missing decision changes scope, data rights, externally visible behavior, cost or irreversible actions. Existing authorization persists; do not insert an approval step after every task.

## Work loop

1. Inspect the repository and existing local instructions. Preserve unrelated work.
2. Select the earliest ready task from TASKS; honor dependencies. Record it in STATUS.
3. State the requirement IDs, proposed change and acceptance check.
4. Implement a small complete feature slice, including loading, empty and failure states.
5. Run the narrow meaningful checks for that behavior. Distinguish mocked-provider checks from a real-provider integration run.
6. Inspect the running UI for user-facing changes when browser tools are available. If unavailable, state that visual verification was not performed.
7. Record files changed, actual command results, requirement coverage and remaining blockers. Mark a task complete only when its acceptance check has evidence.
8. Continue to the next ready task within authorization. A model-training blocker does not block unrelated product work.

Keep progress updates concise and frequent. Commit coherent work when repository policy or the user authorizes it. Do not use git resets or destructive cleanup to hide problems.

## Product constraints

- Use the chosen stack. Do not add a second database, Redis, Kubernetes, microservices, an agent framework or another UI framework without a demonstrated need.
- The app uses a deterministic orchestration pipeline with replaceable model adapters.
- No mock provider in a public live deployment. Test fixtures and a clearly labeled prerecorded sample mode are permitted.
- Each analysis records model provider, revision, model ID, prompt/rubric versions and processing status.
- No silent provider fallback. Unavailable inference is an error or explicitly labeled configured fallback.
- A generated paragraph is not classifier attribution. Label evidence by method and keep predictions separate from reviewer decisions.
- All public-demo reports are synthetic or cleared public material. Real sponsor data requires appropriate authorization and a private deployment.
- No operational safety approvals or automatic machinery/control actions.

## Data and model constraints

- Never invent real reports, citations, source IDs, expert review, metrics, training runs, checkpoint files or deployment URLs.
- Preserve source access/rights uncertainty. Do not auto-mark every public page as training-cleared.
- Split by underlying event before paraphrase, translation, chunking, embedding example retrieval or augmentation.
- No development-set or training-set examples from the final test pool. No test examples in RAG or few-shot prompts.
- Unknown SIF labels do not become negative labels. Unreviewed rule labels do not become negative labels.
- Source identifiers, titles containing outcomes, original severity labels and investigator recommendations do not enter the precursor-classification input.
- No model promotion from a falling training loss alone.
- Do not overwrite failed experiments. Save data/model revisions, seeds, full configuration and dependency locks.
- Raw training records and checkpoints stay out of ordinary git commits. Use controlled data/model storage and record hashes.

## Tool and dependency discipline

Pin compatible dependency versions after a smoke test; do not claim compatibility because packages install. Keep training and serving dependency sets separate. On the student's 8 GB laptop, run one development stack at a time and avoid downloading a generative model unless requested.

Read current official documentation for changed APIs. Example commands in FINE_TUNING_GUIDE are requested interfaces to implement, not scripts already supplied. Create and test those interfaces before telling the user to run them.

No secret values in terminal output, reports, commits, screenshots, browser bundles or example configuration. Use environment-variable names and masked checks.

## Autonomous development is not unrestricted external authority

Implement reversible local changes and tests within the request. Prepare deployable artifacts before requesting a new paid commitment. Honor an already granted deployment or spending authorization. Do not send emails, sponsor requests or messages without explicit authorization. Do not weaken tests or change access rules just to obtain approval.

Use one lead agent by default. Spawn other agents only when the live user or applicable environment instructions permit it; if permitted, assign disjoint files, a bounded deliverable and an integration owner. “Agentic development” does not require many simultaneous agents.

## Definition of done for every task

The specified behavior exists, the relevant check passes, failures are visible, persistence/access boundaries are verified when affected, and STATUS links to actual evidence. “Looks complete,” generated tests that were never run, TODO buttons, and a successful build alone are insufficient.
