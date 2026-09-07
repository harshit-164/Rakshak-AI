# Dependency-ordered implementation tasks

All tasks are **not started**. The pack contains specifications only. TSK identifiers are work items; R identifiers refer to requirements; T identifiers refer to checks in TEST_PLAN.

Mark a checkbox only when the named acceptance evidence exists. Update STATUS with in-progress/blocked details and actual paths. Continue ready local tasks when an external prerequisite is missing.

## M0 — Project and contracts

- [x] **TSK01 — Scaffold and configuration.** Dependencies: none. Create the chosen repo layout, dependency locks, development instructions, environment template, lint/type/build commands and CI skeleton. Evidence: clean install and build; no secrets. Requirements: R15/R16.
- [x] **TSK02 — Shared schemas and fixtures.** Dependencies: TSK01. Implement SPECS in Pydantic, generate TypeScript contracts, parse a valid result and reject invalid taxonomy/provenance. Evidence: T02/T05/T06 contract checks. Requirements: R02/R05/R06.
- [ ] **TSK03 — Database, auth and isolation.** Dependencies: TSK02. Create migrations/RLS/owner-preserving foreign keys, anonymous demo entry and quota counters. Evidence: T01 and access aspects of T16. Requirements: R01/R16.

## M1 — One complete real-inference flow

- [ ] **TSK04 — Report submission and durable queue.** Dependencies: TSK03. Implement report/version routes, jobs, idempotency, leases, retry semantics and worker startup recovery. Evidence: T02/T09 on real Postgres. Requirements: R02/R09.
- [ ] **TSK05 — Hosted baseline and evidence validation.** Dependencies: TSK02/TSK04. Implement the model adapter with versioned prompt/reference bundle, JSON validation, verified evidence and unknown/failure handling. Evidence: T03/T04/T05/T06, including one live call when credentials are provided. Requirements: R03–R06.
- [ ] **TSK06 — Analyze UI.** Dependencies: TSK05. Build paste → job progress → persisted result → reopen flow, mobile/error/unknown states and visible model identity. Evidence: browser golden path and T15. Requirements: R02–R06/R15.
- [ ] **TSK07 — First deployable preview.** Dependencies: TSK06. Prepare frontend/backend deployment configuration and measured resource needs. Deploy when account/budget authorization is present. Evidence: live incognito flow or exact external blocker; do not claim deployed until live. Requirements: R16/R17.

## M2 — Review and dashboard

- [ ] **TSK08 — Review history and conflicts.** Dependencies: TSK06. Implement append-only reviews, corrections and current-version behavior. Evidence: T07. Requirements: R07.
- [ ] **TSK09 — CSV import and export.** Dependencies: TSK04/TSK08. Implement bounded import with row mapping, reconciliation, safe export and isolated data deletion. Evidence: T08/T11 plus deletion authorization check. Requirements: R08/R11/R16.
- [ ] **TSK10 — Dashboard.** Dependencies: TSK08. Implement reviewed/predicted views, density, coverage, unknown/failed counts and tag patterns. Evidence: T10 arithmetic fixture and UI inspection. Requirements: R10/R15.
- [ ] **TSK11 — Release resilience pass.** Dependencies: TSK09/TSK10. Test outages, worker recovery, rate limits, mobile access and actual production configuration. Evidence: T01–T11/T15–T17 as applicable. Requirements: R01–R11/R15–R17.

## M3 — Dataset and trained encoder

This work can proceed alongside M1/M2. Harshit/team supplies downloaded eligible reports and reviewed labels; the agent builds the tools.

- [ ] **TSK12 — Source register and parsing.** Dependencies: TSK01. Create source register/extractors, manual review export and provenance storage. Evidence: five inspected extracted records, no fabricated labels/permissions. Requirements: R13.
- [ ] **TSK13 — Annotation and split release.** Dependencies: TSK12. Review seed, resolve duplicates, encode masks, freeze event groups/splits and write dataset card. Evidence: T13 and actual label/source counts. Requirements: R13.
- [ ] **TSK14 — Reproducible baselines.** Dependencies: TSK13/TSK05. Implement TF-IDF and fixed-prompt comparators on the same split/input view. Evidence: validation report and metric arithmetic checks. Requirements: R14.
- [ ] **TSK15 — Encoder notebook and SIF training.** Dependencies: TSK13/TSK14. Implement notebook/shared modules, debug tiny subset, run bounded GPU fine-tuning when available and save artifacts. Evidence: changed weights, logs, config and reload. Requirements: R12–R14.
- [ ] **TSK16 — Rule head and masking.** Dependencies: TSK15 and reviewed rule targets. Add shared nine-label head, assessed-label masks and unsupported-rule handling. Evidence: mask invariance tests, taxonomy checks and per-rule validation support. Requirements: R05/R12–R14.
- [ ] **TSK17 — Frozen evaluation and CPU adapter.** Dependencies: TSK15, plus TSK16 if deploying trained tags. Freeze candidate settings, evaluate final test, export artifact, benchmark CPU and integrate adapter. Evidence: T12–T14, chosen-model rationale and measured latency/memory. Requirements: R12–R14.
- [ ] **TSK18 — Model deployment and pitch evidence.** Dependencies: TSK11/TSK17. Load selected model in the real environment; record demo and prepare six-slide evidence outline. Evidence: T17, live manifest match and truthful model card. Requirements: R17.

## M4 — Requested QLoRA learning experiment

- [ ] **TSK19 — QLoRA dataset and notebook.** Dependencies: TSK13/TSK14. Create prompt/completion serializer, mask/length checks, hardware preflight and 5–10-step smoke run. Evidence: eligible split hashes, token masks and measured VRAM/time. Requirements: R13/R14.
- [ ] **TSK20 — Train, reload and compare Qwen adapter.** Dependencies: TSK19 and an available authorized GPU session. Save base revision plus adapter; compare Q0/Q1 on frozen data with matching prompts. Evidence: adapter files, clean reload and real evaluation; separately record whether this reuse of the existing test pool was predeclared. Requirements: R12–R14.
- [ ] **TSK21 — Optional Qwen serving decision.** Dependencies: TSK20. Measure CPU/GPU serving and cost. Promote only if supported; otherwise document the completed research experiment separately from the deployed engine. Evidence: decision entry and resource measurements. Requirements: R12/R14/R17.

## M5 — Completion audit

- [ ] **TSK22 — Requirements/evidence audit.** Dependencies: applicable release tasks above. Verify every claimed completed requirement has passing evidence. List incomplete optional work, actual data limits, costs and model failures. Publish nothing unsupported. Evidence: updated STATUS and release checklist. Requirements: R01–R17.

## Suggested team allocation

Harshit: product decisions, integration and deployment. One teammate: frontend. One: API/database. Two: source collection and independent annotation, with mentor adjudication where available. One: training/evaluation and demo verification. People can combine roles, but independent checks should not become self-certification.

Suggested sequencing: days 1–3 M0/M1; days 4–7 M2; data collection starts day 1 and controls the model schedule. Allow another 1–2 weeks for a meaningful reviewed-data/training cycle if possible. Do not wait until the last day to discover deployment constraints.
