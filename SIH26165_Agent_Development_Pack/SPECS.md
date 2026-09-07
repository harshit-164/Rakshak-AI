# Authoritative implementation specifications

Version 1.0 · schema_version: 1.0 · label_guide_version: sif-pilot-v1

This document owns contract names, constants and runtime behavior. Examples are illustrative synthetic records; no JSON object below is an executed result.

## Requirements and acceptance map

| ID | Required behavior | Acceptance check |
|---|---|---|
| R01 | Authenticated isolated demo sessions; user A cannot read/write B's rows. | T01 |
| R02 | Validate and persist a new report without silently rewriting it. | T02 |
| R03 | Run actual versioned inference through a stable adapter. | T03 |
| R04 | Preserve unknown/abstention and provider failure as different states. | T04 |
| R05 | Allow multiple, zero or unassessed Life-Saving Rules. | T05 |
| R06 | Verify quoted evidence and reference IDs; retain method/provenance. | T06 |
| R07 | Append reviews and retain original predictions. | T07 |
| R08 | Import bounded CSV batches with row errors and progress. | T08 |
| R09 | Durable idempotent jobs recover safely from a worker restart. | T09 |
| R10 | Dashboard counts reconcile with stored reviewed or predicted data. | T10 |
| R11 | Safe CSV export includes provenance and latest review separately. | T11 |
| R12 | Load trained artifacts with correct revision and thresholds. | T12 |
| R13 | Enforce event-level split, annotation masks and training eligibility. | T13 |
| R14 | Publish reproducible evaluation and model-selection evidence. | T14 |
| R15 | Responsive, accessible UI with real loading/error/empty states. | T15 |
| R16 | Enforce security, request limits and deployment configuration. | T16 |
| R17 | Public demo and pitch identify actual implementation/model status. | T17 |

## Default pilot limits

| Setting | Default |
|---|---|
| Narrative | 20–8,000 Unicode code points after rejecting blank-only content |
| API body limit | 512 KiB |
| CSV | UTF-8, up to 20 data rows, 256 KiB, quoted multiline fields supported |
| Activity/site | nullable; max 120 code points each |
| Report date | nullable ISO calendar date; no invented date |
| Active jobs | at most 2 queued/running jobs per user |
| Worker inference concurrency | 1 initially |
| Rate limits | 10 report submissions/minute/user; 100 analyzed reports/day/user |
| Provider timeout | 45 seconds per call; bounded transient retry only |
| Worker lease | 180 seconds; heartbeat every 30 seconds |
| Job attempts | max 2 automatic attempts; manual retry is a new explicit action |
| Polling | start at 2 seconds, back off to at most 10 seconds |
| List pagination | default 25, maximum 100 records/page |
| Aggregate ranking | show groups with at least 10 eligible records; smaller groups listed as insufficient sample |
| Test split seed | 42; persist actual group assignment, not only the seed |
| Public demo retention | 30 days; configurable, with caller-owned deletion available |
| Supported language | English initially; other/uncertain language routes to review |

A batch counts each valid report toward quotas. Changes to these defaults must update this table and relevant tests.

## Canonical taxonomy

Keep this exact array order in model artifacts and API output:

| ID | Display label |
|---|---|
| bypassing_safety_controls | Bypassing safety controls |
| confined_space | Confined space |
| driving | Driving |
| energy_isolation | Energy isolation |
| hot_work | Hot work |
| line_of_fire | Line of fire |
| safe_mechanical_lifting | Safe mechanical lifting |
| work_authorisation | Work authorisation |
| working_at_height | Working at height |

Source: IOGP S25. IDs are application identifiers, not altered IOGP rule wording.

SIF labels: **yes**, **no**, **unknown**. Unknown means insufficient evidence, model abstention, unsupported input or unsupported length; it does not mean an API failed. Rule relevance is separate from confirmed breach. rules_assessment is complete / partial / unknown. The assessed/unassessed partition must cover the canonical taxonomy without contradictions. Complete requires no unassessed IDs; partial lists every unassessed ID; unknown treats all rule IDs as unassessed. Empty rule list with assessment complete means “none identified”; partial means only supported/assessed categories were considered, with unassessed_rule_ids listed; unknown means “not determined.” Never interpret an unsupported category as a negative tag.

## Persistent entities

Every user-owned row has id, owner_id, created_at and updated_at. IDs are server-generated UUIDs. Foreign keys must preserve the same owner, enforced in SQL as well as application code.

- **reports:** owner_id, report_group_id, version, narrative, normalized_input, normalization_version, narrative_sha256, activity, site, report_date, is_synthetic, demo_dataset_id, predecessor_id. Immutable input after creation.
- **analysis_jobs:** report_id, engine_mode, status, idempotency_key, request_sha256, attempt_count, lease_token, lease_expires_at, heartbeat_at, error_code, provider_attempt_metadata.
- **analyses:** report_id, job_id, structured result, model_manifest_sha256, input_sha256, duration_ms. Immutable after completion; unique job_id.
- **reviews:** analysis_id, reviewer_id, sif_label, relevant_rule_ids, rules_assessment, unassessed_rule_ids, confirmed_breach_ids, barrier_tags, note, evidence_edits, version. Append-only; note required, 10–2,000 code points.
- **batches:** owner_id, valid report/job IDs, rejected row numbers/reasons, totals, status. Do not persist unnecessary raw uploads.
- **reference_documents:** curated admin-controlled source ID, source URL, title, edition, rights status, document hash, approved passages. Guest users cannot write.
- **model_registry:** admin-controlled immutable manifests and one active model reference.
- **usage_buckets:** atomic rate/usage counters. A migration sets retention and access rules.

Training datasets are offline versioned exports, not direct reads of the public demo database. Guest reviews do not automatically become training labels.

## Public API (FastAPI under /v1; Next.js proxies authenticated calls)

All user routes require a valid Supabase user JWT, including anonymous authenticated users. Derive owner_id from the verified subject; reject owner_id in request bodies. Use issuer/audience/signature/expiry validation. Return 404 for another user's object.

| Method / route | Request and response |
|---|---|
| GET /health/live | Public minimal process liveness; no secrets or internal paths |
| GET /health/ready | Minimal readiness; 503 until dependencies/selected model are usable |
| GET /v1/capabilities | Safe list of available engines, schema/rubric versions, current model display name and limits |
| POST /v1/reports | Report input + Idempotency-Key header; 201 with report_id, or original response for exact retry |
| POST /v1/reports/{id}/analyses | engine_mode + Idempotency-Key; 202 with job_id/status |
| GET /v1/jobs/{id} | Job status, safe error and analysis_id when complete |
| GET /v1/reports | Paginated report summaries and latest assessment/review; allowlisted filters |
| GET /v1/reports/{id} | Input versions, analyses and authorized review history |
| POST /v1/analyses/{id}/reviews | Latest review version precondition plus proposed review; 201 or 409 conflict |
| POST /v1/imports | CSV multipart upload; validate whole structure, then create valid row jobs; 202 batch_id + rejected rows |
| GET /v1/imports/{id} | Total/queued/running/completed/failed/rejected counts and row mapping |
| GET /v1/dashboard | mode=reviewed or predicted, identical allowlisted filters |
| GET /v1/export | Authorized filtered CSV; spreadsheet-formula escaping |
| DELETE /v1/demo-session/data | Delete only caller-owned demo content and cancel own queued jobs; require explicit UI confirmation |

Errors use {"error":{"code":"...","message":"...","retryable":false,"request_id":"..."}}.
Use 400 malformed syntax, 401 invalid session, 404 unavailable resource, 409 conflict, 413 size limit, 422 semantic validation, 429 quota, 503 unavailable backend. Distinguish an external inference failure from an unknown safety assessment.

The user-facing app never receives privileged model-storage or database credentials.

## Model adapter result

Engine modes: **hosted_baseline**, **encoder**, **qwen_adapter**, **recorded_sample**.
The last mode is only for labeled demonstration playback; it cannot accept new reports or contribute to live metrics.

The adapter receives only normalized narrative plus optionally provided activity. Site/date support dashboard grouping and do not enter the initial classifier. Source outcome, labels, review text and original source metadata are prohibited model features.

Every successful result follows this shape:

~~~json
{
  "schema_version": "1.0",
  "sif_label": "yes",
  "abstain_reasons": [],
  "model_score": null,
  "score_kind": "none",
  "relevant_rule_ids": ["line_of_fire", "safe_mechanical_lifting"],
  "rules_assessment": "complete",
  "unassessed_rule_ids": [],
  "rule_scores": null,
  "precursors": [
    {"tag": "overhead_load_exposure", "evidence_ids": ["e1"]}
  ],
  "barriers": [
    {"tag": "separation_from_suspended_load", "state": "failed", "evidence_ids": ["e1"]}
  ],
  "evidence": [
    {
      "id": "e1",
      "field": "narrative",
      "quote": "A suspended load passed directly above a worker",
      "method": "llm_extracted"
    }
  ],
  "missing_information": [],
  "summary": "Potential serious harm requires reviewer attention.",
  "references": [{"source_id": "S25", "passage_id": "curated-lifting-001"}],
  "review_status": "pending",
  "provenance": {
    "engine_mode": "hosted_baseline",
    "model_id": "CONFIGURED_AT_RUNTIME",
    "model_revision": "RECORDED_AT_RUNTIME",
    "prompt_version": "sif-analysis-v1",
    "label_guide_version": "sif-pilot-v1",
    "auxiliary_models": [],
    "inference_is_live": true
  }
}
~~~

CONFIGURED_AT_RUNTIME and RECORDED_AT_RUNTIME are explanatory placeholders that must be rejected in deployed results. For a hosted API that does not expose a revision, record the configured model ID plus provider_revision_unavailable explicitly. Never invent an exact provider revision. The example passage ID requires a real curated entry; examples do not create reference records.

Evidence quotes must occur verbatim in the specified normalized input field. Generate highlight offsets server-side after verification; return offsets if useful. Keep normalization deterministic and versioned. If a quote appears several times, disambiguate the occurrence before highlighting. Never trust LLM-supplied offsets.

If another model extracts evidence or writes a summary, auxiliary_models records its purpose, provider, model_id and revision status. The primary classifier identity remains unchanged. rule_scores is null when unavailable, or a map of canonical IDs to raw nullable scores; unsupported IDs have null, not zero.

Barrier state: failed / missing / present / unknown. “Missing” means explicitly absent; silence is unknown. Evidence method: llm_extracted / rule_matched / reviewer. Confirmed breaches are reviewer fields, not automatically inferred by a tag.

## Decision policy

For encoder mode, obtain a binary SIF score and apply **versioned low/high thresholds chosen on validation data**: score ≤ low gives no; score ≥ high gives yes; between gives unknown. Require 0 ≤ low < high ≤ 1 and finite scores. No default pair may be presented as validated. Store raw score for research with score_kind=uncalibrated_model_score unless independently calibrated. Never display it as accident probability.

Reject unsupported/empty input before inference. If a tokenizer limit is exceeded, do not silently truncate: produce unknown with input_too_long_for_model, or route to an explicitly configured full-text baseline and identify that engine. This first release does not implement unvalidated max-over-chunk classification.

For hosted/Qwen modes, parse schema-constrained labels; model_score remains null. Self-reported confidence is discarded. A model can abstain with explicit reasons. Independent evidence verification removes unsupported quotes/references and marks evidence_unavailable. If no defensible evidence for a proposed definitive label remains, return unknown while preserving the raw provider output privately for debugging only if allowed.

Model unavailability is job failure, not unknown. A fallback is disabled by default. If enabled, show the actual provider and fallback_reason; never attribute a hosted answer to fine-tuned weights.

## Dashboard definitions

Default mode=reviewed uses each report group's latest input version and latest human review of an analysis for that version. An old review is not applied to a revised narrative. Predicted mode uses the latest completed live analysis of the latest version and is labeled provisional.

For each site/activity, count distinct report groups:
- eligible_yes and eligible_no are definitive labels in the chosen mode.
- unknown_count is separate; unreviewed_count is also separate in reviewed mode.
- queued/running/failed analysis counts are separate from safety-label unknowns.
- density = eligible_yes / (eligible_yes + eligible_no); null if denominator is zero.
- review_coverage = reviewed report groups / total filtered report groups.
- display numerator, denominator, unknowns, unreviewed count, date range and synthetic status.
- ranking requires at least 10 eligible reports; ties use denominator descending, then group name.
- reports with absent site/activity stay in an “Unspecified” group.
- do not mix synthetic and real records by default; require an explicit filter choice.
- density is a descriptive proportion among reports, not exposure-adjusted operational risk.

Aggregate only after ownership and filters are applied. Rule and barrier charts count distinct reports per tag; their sums can exceed total reports because tags are multi-label. Reviewed mode uses reviewer-approved tags only.

## Job and review states

Job: queued → running → completed or failed. Expired running leases can be reclaimed within the attempt limit. Atomic claims, lease-token checks, unique outputs and idempotent finalization prevent duplicate analyses. Remote provider calls may still be repeated after a crash; record attempts and possible repeated cost rather than promising exactly-once execution.

Review: pending → reviewed; later corrections append another review. Require the expected latest review version to prevent silent overwrites. Any text revision produces a new report version; prior analyses/reviews remain historical.

Future expansion must preserve these contracts or increment schema_version and include migration notes.
