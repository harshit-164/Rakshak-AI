# TSK04 — Report submission and durable queue evidence

State: in progress; implementation and local tests pass, real-Postgres recovery evidence is pending.

Implemented behavior:

- Strict report and job routes with caller-token RLS access and server-owned identity.
- Deterministic NFC/line-ending normalization while retaining the original narrative.
- Canonical request hashes and exact idempotent replay; changed payloads return 409.
- Durable Postgres job states, atomic claims, 180-second leases, heartbeat, two attempts,
  transactional idempotent finalization, and safe failure codes.
- Worker attempt metadata explicitly records that a provider call may repeat after a crash.
- Quotas are consumed only for newly created resources, never exact idempotent replays.

Local checks on 3 September 2026:

- `npm run db:test`: PASS.
- `pytest services/api/tests`: 29 passed across the current API suite.
- Worker tests prove successful finalization and prove provider unavailability becomes a
  failed job rather than an `unknown` safety result.
- A lost finalization response leaves the running lease intact for expiry/reclaim; it does not
  prematurely convert a potentially committed result into a failed job.
- Running FastAPI returned 200 liveness, fail-closed 503 readiness, and a request-ID-bearing
  401 error envelope for an unauthenticated resource request.

Acceptance not yet met:

- T09 kill/reclaim cases and stored-analysis uniqueness must run against the actual Supabase
  Postgres service. No real provider call was made.
