# TSK03 — Database, authentication, and isolation evidence

State: in progress; local contract evidence passes, real Supabase acceptance is pending.

Implemented paths:

- `supabase/migrations/202609030001_core_schema.sql`
- `supabase/migrations/202609030002_queue_functions.sql`
- `supabase/migrations/202609030003_atomic_demo_quotas.sql`
- `services/api/app/auth.py`
- `services/api/app/persistence.py`
- `tests/database-isolation.mjs`
- `services/api/tests/test_auth.py`
- `services/api/tests/test_routes.py`

Verified locally on 3 September 2026:

- PGlite applied every migration and passed two-subject owner isolation, RLS rejection,
  idempotent report/job creation, the 10-report minute bucket, the 100-analysis daily
  counter primitive, and the two-active-job boundary.
- JWT tests verify RS256 issuer/audience/expiry/role/subject and legacy Supabase token
  validation through the Auth server. No JWT shared secret is embedded.
- API tests return the same 404 shape for unavailable/other-owner report IDs and reject
  missing bearer tokens with the specified error envelope.

Acceptance not yet met:

- T01 must be repeated with two actual anonymous sessions against a test Supabase project.
- The remote-project RLS and abuse-protection configuration cannot be verified without a
  project URL and credentials. TSK03 therefore remains unchecked.
