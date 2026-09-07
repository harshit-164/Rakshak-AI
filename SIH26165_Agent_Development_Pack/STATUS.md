# Project status and evidence

Last updated: 3 September 2026
Pack version: 1.0

## Current state

| Area | Actual status |
|---|---|
| Specification pack | Created |
| Application implementation | TSK01–TSK02 verified; TSK03–TSK07 implemented locally but acceptance-blocked |
| Sourcebook | Read; catalogue only |
| Downloaded incident corpus | Not supplied by this pack |
| Reviewed training records | Not created |
| Frozen train/validation/test split | Not created |
| TF-IDF baseline | Not run |
| Hosted baseline integration | Gemini adapter/worker implemented; deterministic tests pass; live call not run |
| Encoder fine-tuning | Not run |
| QLoRA fine-tuning | Not run |
| Model evaluation | Not run |
| Public deployment | Render/Vercel configuration created; no external deployment made |
| Credentials/cloud budget | Not configured or authorized by this pack |

## Active work

Current task: credentialed acceptance for TSK03–TSK07 (externally blocked).
Next ready local task: complete TSK12 source extraction/review tooling while credentials are obtained.
Parallel human action: obtain a small eligible source batch and identify who can review safety labels.

## Implementation evidence

### TSK01 — Scaffold and configuration

- Task ID and requirement/check IDs: TSK01; R15/R16; scaffold portion of T15/T16.
- State: verified locally; production credentials and deployment remain later tasks.
- Code revision and changed paths: no Git revision exists yet; root workspace, `apps/web`,
  `services/api`, `packages/contracts`, `configs`, CI, and repository guardrails created.
- What behavior now works: locked Next.js/TypeScript and FastAPI/Python workspaces, public
  liveness, fail-closed readiness, responsive product shell, and documented secret boundary.
- Actual commands/checks and outcomes: `npm install`; `npm audit --audit-level=high` (0
  vulnerabilities after upgrading Vitest 3.2.4 to 3.2.7); `npm run lint`; `npm run typecheck`;
  `npm run test` (1 web test); `npm run build` (Next.js 16.3.4 production build); `ruff check`;
  `mypy` (0 issues); `pytest` (included in current 12-test API suite).
- Live-provider vs mock-provider coverage: no provider used in TSK01; readiness is 503 when
  Gemini/Supabase are unconfigured.
- Screenshots/evidence paths: live browser inspection at desktop and 390 px; semantic
  landmarks present and browser console had no warnings/errors. A horizontal mobile overflow
  was found and fixed before verification. See `evidence/TSK01.md`.
- Remaining issue or external dependency: Supabase project and Gemini key are not configured.
- Next ready task: TSK02 (completed), then TSK03.

### TSK02 — Shared schemas and fixtures

- Task ID and requirement/check IDs: TSK02; R02/R05/R06; contract portions of T02/T05/T06.
- State: verified.
- Code revision and changed paths: `services/api/app/contracts.py`, validation/OpenAPI
  modules, generated `packages/contracts/openapi.json` and `src/api.d.ts`, contract tests.
- What behavior now works: strict report/model schemas, canonical nine-rule ordering,
  assessed/unassessed invariants, unknown handling, runtime provenance validation, exact-quote
  and allowlisted-passage verification, and generated browser types.
- Actual commands/checks and outcomes: `ruff check` passed; `mypy` passed; `pytest` passed
  12 tests; two consecutive `npm run contracts:generate` results had matching SHA-256 hashes;
  workspace TypeScript checking passed.
- Live-provider vs mock-provider coverage: deterministic fixtures only; no live inference claim.
- Screenshots/evidence paths: non-visual contract task; see `evidence/TSK02.md`.
- Remaining issue or external dependency: persistence and real provider execution belong to
  TSK03–TSK05.
- Next ready task: TSK03.

### TSK03–TSK07 — First complete inference slice

- Task ID and requirement/check IDs: TSK03–TSK07; R01–R06/R09/R15–R17;
  local portions of T01–T06/T09/T15–T17.
- State: implemented and locally verified where possible; task checkboxes remain open because
  real Supabase, live Gemini, restart recovery, and deployed incognito evidence do not exist.
- Code revision and changed paths: no Git revision exists; see `evidence/TSK03.md` through
  `evidence/TSK07.md` for code and migration paths.
- What behavior now works: JWT verification; owner-scoped persistence; atomic quotas;
  idempotent durable jobs; leased worker; Gemini adapter; evidence verification; anonymous
  browser flow; result/reopen screen; API proxy; Docker/Render/Vercel configuration.
- Actual commands/checks and outcomes: Ruff passed; strict mypy passed; API pytest 29 passed;
  embedded migration/isolation/quota test passed; workspace lint/typecheck/test passed; Next.js
  production build passed; npm audit reported zero vulnerabilities; running proxy reached
  running FastAPI capabilities; desktop and
  390×844 setup-state inspection passed with no browser console warnings/errors.
- Live-provider vs mock-provider coverage: Gemini request/response and worker behavior use
  injected deterministic doubles only. `inference_is_live=true` is asserted only for adapter
  outputs that represent the hosted execution path; no completed live call is claimed.
- Remaining issue or external dependency: test Supabase URL/public/service-role credentials,
  enabled anonymous auth, Gemini key, and deployment/budget authorization. Docker tooling is
  absent locally, so the image has not been executed.
- Next ready task: complete TSK12 locally; run T01/T03/T09/T15–T17 immediately after credentials.

### TSK12 — Source register and draft extraction

- State: in progress; four quarantined records drafted and all supplied PDF pages inspected.
- Evidence: `evidence/TSK12.md`, `configs/references/source-register.v1.json`, and ignored local
  `data/draft_extractions.jsonl`.
- Remaining issue: a fifth record, human review, and rights clearance are still required.

## Task evidence log template

For each task, append:
- Task ID and requirement/check IDs:
- State: not started / in progress / blocked / verified
- Code revision and changed paths:
- What behavior now works:
- Actual commands/checks and outcomes:
- Live-provider vs mock-provider coverage:
- Screenshots/evidence paths:
- Remaining issue or external dependency:
- Next ready task:

## Model experiment log template

- Run ID:
- Actual base model and revision:
- Dataset/split hashes and counts:
- Hardware:
- Training configuration and dependency lock:
- Start/end time and measured resource use:
- Artifact paths/checksums:
- Clean reload result:
- Validation/final-test report:
- Decision and limits:

No experiment entries exist yet. Do not fill this table with expected metrics.

## Release evidence template

- App URL and revision:
- Active model manifest/revision:
- Tested date and environment:
- Passed checks:
- Outstanding checks:
- Data/reviewer limitations:
- Live vs recorded demonstration paths:
- Measured latency/cost:
- Rollback target:

## Change control

When a contract changes, record its rationale in DECISIONS, update SPECS and affected tasks/checks, then run the relevant consistency checks. Retain failures and previous experiment reports.
