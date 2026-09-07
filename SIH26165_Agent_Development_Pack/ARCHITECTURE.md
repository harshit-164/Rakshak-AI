# Architecture and model integration

## Chosen components

- **Next.js + TypeScript:** Analyze, Reports/Review and Dashboard views; Supabase session handling; a same-origin API proxy.
- **FastAPI + Python:** schema validation, business rules, model adapters, evidence checks and database operations.
- **Supabase Postgres/Auth:** persistent reports, analyses, reviews, job queue, model registry and isolated anonymous demo users.
- **PyTorch/Transformers:** offline training and CPU encoder inference. Keep CUDA training dependencies out of the serving image.
- **Recharts:** charts computed from API aggregates.
- **Gemini API:** initial hosted baseline and optional evidence extraction, with server-side credentials.
- **Colab:** interactive GPU training, not public hosting.
- **Vercel + Render:** default frontend and container-backend deployment plan. Final backend size is selected after memory/latency measurement. No paid resource is provisioned by the planning pack.

~~~mermaid
flowchart TD
  A["Next.js app and session"] --> B["FastAPI API"]
  B --> C[("Supabase records and jobs")]
  C --> D["Single inference worker"]
  D --> E["Selected model adapter"]
  F["Curated references"] --> E
  E --> D
  D --> C
  C --> B
~~~

The graph depicts component responsibility; it is not a request for autonomous agents to reason about safety.

## Repository layout to implement

| Path | Responsibility |
|---|---|
| apps/web/ | Next.js frontend, session and API proxy |
| services/api/ | FastAPI routes, worker and adapter code |
| packages/contracts/ | Generated TypeScript types and shared JSON fixtures |
| ml/ | Data validation, splitting, baseline, training and evaluation modules |
| notebooks/ | Numbered Colab notebooks calling the same ml modules |
| configs/ | Versioned non-secret model/data settings |
| supabase/migrations/ | Schema, RLS, owner-preserving foreign keys and restricted queue functions |
| tests/ | Contract, integration and golden-path browser tests |
| artifacts/manifests/ | Small model/dataset manifests permitted in git |
| evidence/ | Test reports and sanitized screenshots; no sensitive narratives |
| data/ and artifacts/models/ | Ignored local data/checkpoints; controlled persistent copies elsewhere |

These directories and scripts do not yet exist in this pack. Task TSK01 creates the application scaffold.

## Avoid duplicate contracts

Define Pydantic request/result types in the API. Generate OpenAPI/JSON schemas and TypeScript client types from them; do not maintain independently drifting field names. Add a CI check for generated-contract drift and shared example parsing. The Markdown contract remains the requirement source until a versioned change is documented.

## End-to-end sequence

1. Browser obtains an anonymous Supabase authenticated session.
2. Next.js forwards the user JWT and a request ID to FastAPI; no shared administrator credential is exposed.
3. FastAPI verifies identity and atomically creates a report and/or job under the user.
4. The worker claims a queued job using a lease and loads the selected versioned model.
5. The adapter performs real inference. The processor validates schema, taxonomy, evidence and abstention policy.
6. Persist the completed analysis and finalize the job in a transaction.
7. Browser polling displays the saved result. Review submission creates an append-only record.
8. Dashboard/export queries apply the same ownership, version and filter rules.

## Durable worker design

For the small demo, run one API process and one background worker loop in the same container, with inference dispatched off the event loop. Use Postgres as the durable queue. No job's only copy may live in a Next.js request or Python memory.

Implement claim/heartbeat/finalize operations as restricted database functions. A worker-specific secret/service credential is server-only. Only those worker/admin paths may use elevated access. Public request handlers use the caller JWT for PostgREST/RPC so RLS still applies.

Claims use an atomic SQL update or FOR UPDATE SKIP LOCKED. Finalization requires matching job ID and lease token. The report owner is read from the job, never caller-supplied. Unique job_id on analyses and transactional writes make repeat finalization harmless. Reclaim expired jobs on startup. An exhausted attempt limit becomes failed, with a visible retry action.

In-process execution is acceptable for this bounded pilot only because queue state is durable and restart-tested. A larger deployment can separate the worker container without changing the API.

## Model adapter boundary

All adapters implement load(manifest), health(), analyze(input, reference_bundle) and unload(). They return the SPECS result contract. Use one active encoder model per worker; avoid duplicate copies from multiple web-server workers.

- hosted_baseline: prompted API result with verified quotes and fixed reference IDs.
- encoder: DeBERTa SIF head and optional rule head; reference/extraction module supplements the classification.
- qwen_adapter: exact base revision + saved LoRA adapter; same task/output contract.
- recorded_sample: separate playback pathway, never new-input inference.

Maintain a model registry manifest with engine, revision/hash, taxonomy order, normalizer version, max input tokens, thresholds, calibration status and evaluation artifact hash. Readiness fails when requested artifacts or thresholds are missing.

## Evidence and explanations

A classifier's logits do not identify exact supporting sentences. For P0, use a constrained extraction call or deterministic rule matching to suggest evidence, and verify every quote against the narrative. Clearly identify the evidence method. Do not call generated text a faithful causal explanation of the encoder.

For the own-model demonstration, provide an **encoder-only mode** with model scores/tags plus verified matching excerpts and reviewer notes. If an optional LLM creates a summary, label that separate contribution in model provenance and the demo.

No retrieval system is needed for nine short rule definitions. Start with a versioned approved reference bundle. Add pgvector similar-case retrieval only when the corpus warrants it. If added, index eligible training/reference material only; exclude validation/test examples, post-event labels and private unapproved content.

## Serving resource assumptions

Use CPU batch size 1 and one inference concurrency slot initially. Benchmark the actual process RSS, peak memory, cold start and warm latency. A 2–4 GB backend memory envelope is a starting planning target for the encoder, not a guarantee; select the host after measurement with headroom.

Train QLoRA on an available GPU. Serving it is a separate resource decision: test CPU latency or use an explicitly budgeted GPU endpoint. Never expect a free Colab session to remain online for judges.

## Local development on 8 GB

Run the frontend and lightweight API first using a real hosted provider with credentials, or labeled fixtures for automated tests. Use a remote development database if local Postgres/Docker competes for RAM. Train remotely and load only the selected encoder locally when measuring CPU behavior. Do not run several large models simultaneously.

## Resilience

Provider timeouts, invalid JSON and model-load failures are surfaced as explicit job states. A configured fallback must be visible. A curated recorded sample is available separately for outage demonstration. The live dashboard never silently mixes playback with computed results.
