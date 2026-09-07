# Security and data handling for the pilot

## Scope

The public prototype processes synthetic or cleared public examples only. It is not connected to Oil India's internal system. An authorized private deployment and appropriate data processing arrangements are prerequisites for sponsor incident records.

Model-assisted safety triage remains subject to human review. No app action authorizes hazardous work, controls machinery, or evaluates named workers.

## Identity and access

Use Supabase anonymous sign-in for one-click demo access. These are authenticated users with distinct IDs; they are not equivalent to unauthenticated use of the public anon key [REF15].

Verify JWT signature, issuer, audience and expiry using the project's supported signing configuration. Do not trust decoded-but-unverified claims. Never accept owner_id or reviewer_id from a client body.

Enable RLS on every exposed user-data table and owner-preserving foreign keys. Browser/ordinary API requests use user-scoped credentials. The worker's service credential is server-only and restricted in code to queue/model-admin operations; add tests proving public routes never use the elevated client.

For SECURITY DEFINER functions, set a safe search_path, avoid dynamic SQL, grant execution only to the required role, and enforce ownership/lease checks. Do not expose a generic privileged RPC.

Model/reference registry writes are maintainer-only. Guest users cannot choose arbitrary model URLs, upload executable weights or change the shared reference bundle.

## Threats and required controls

| Threat | Required control |
|---|---|
| Guessing another user's report/job ID | Ownership + RLS + consistent 404 responses |
| Prompt injection in a report | Treat narrative as untrusted data; no tools/commands in inference; strict schema validation |
| Fabricated evidence/citations | Exact quote checks and allowlisted reference IDs |
| API key exposure | Server-only secrets; inspect built frontend and logs |
| Cost abuse | Atomic per-user quotas, bounded bodies/batches, auth abuse controls and upstream caps |
| CSV formula injection | Neutralize formula/control prefixes when exporting untrusted cells |
| Malicious uploaded document | CSV only initially; no arbitrary URL fetch or document execution |
| Poisoned training labels | Draft vs reviewed labels, provenance, split locks and human review |
| Unsafe model artifact | Trusted immutable source/hash; no unreviewed remote code or user-selected pickle |
| Worker duplication | Lease tokens, idempotent persistence and auditable attempts |
| Sensitive report logging | Request IDs and status metadata; avoid raw narratives in default logs |

User text cannot override the labeling rubric, output schema, provider selection or references. Provider response URLs are not fetched. Public inference has no shell, web, email or database-write tools.

## Input and evidence

Normalize text deterministically without deleting negation. Escape output in the UI. Evidence quotes are matched against the normalized input and never rendered as trusted HTML.

Site names, employee identifiers and post-event outcome metadata are not classifier features. A source citation is provenance, not permission to train or redistribute.

## Data lifecycle

Keep only fields needed for the demo and audit. Provide explicit deletion of the caller's demo data. Cancel queued jobs and prevent late worker writes after deletion. Test cascade/lease races.

Implement a documented, configurable demo retention period, initially 30 days, with a maintainer-controlled cleanup job. Preserve only aggregate service-health metrics without narratives where possible. No automatic deletion of training checkpoints or non-demo project artifacts.

Do not add guest reviews directly to training. Export candidate feedback to a separate review queue, check rights/quality/lineage and create a new dataset version before retraining.

## Logs and errors

Log request ID, engine ID/revision, duration, status, attempt count and safe error code. Do not include access tokens, service keys, full prompts, private narratives or raw provider responses by default. Any debug logging of content must be explicit, access-controlled and short-lived.

Show useful retry/error messages without internal stack traces. An unknown assessment is not an error; a provider outage is not a negative classification.

## Responsible claims

Use “experimental review assistant,” “fine-tuned on N reviewed records,” and “measured on M unseen events” only when supported. No claims of certified compliance, guaranteed prevention, real-time site risk or expert review that did not happen.
