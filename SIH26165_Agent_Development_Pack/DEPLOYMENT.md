# Deployment, costs and release checks

## Deployment decision

Default plan: **Next.js on Vercel, FastAPI container on Render, Supabase Postgres/Auth, trained encoder on the backend CPU**. Train in Colab separately. Render documents FastAPI deployment [REF14]; choose backend memory from measurements, not from the smallest advertised tier.

The initial API-only baseline may need less memory than a loaded transformer. Re-measure when integrating the encoder. The 2–4 GB planning envelope in ARCHITECTURE is a starting point; actual peak RSS plus headroom decides the tier.

No paid resource or account has been created. Harshit confirms the live quote and budget when the implementation is ready to deploy. Existing authorization in a session takes precedence over asking again.

## Why training and hosting are separate

Training can use a temporary notebook GPU. Judges need a stable application endpoint after that notebook ends. Store checkpoints persistently and deploy the selected inference artifact independently.

Do not host the public backend in a free Colab runtime. Colab is designed around interactive notebooks, resources are variable, and its rules restrict certain remote/web-service usage [REF02].

Hugging Face is an alternative, but current Spaces documentation says creating compute-based Docker/Gradio Spaces requires a paid plan, even though CPU Basic has no hourly hardware charge. Current docs also describe inactivity sleep on basic hardware [REF11/REF12]. Recheck eligibility and pricing at setup; do not promise a new free Docker Space.

## Environment variables to implement

| Location | Variable | Purpose |
|---|---|---|
| Frontend | NEXT_PUBLIC_SUPABASE_URL | Public project URL |
| Frontend | NEXT_PUBLIC_SUPABASE_ANON_KEY | Public client key; RLS still required |
| Next server | API_BASE_URL | Backend origin |
| API | SUPABASE_URL, SUPABASE_ANON_KEY | JWT-scoped data operations |
| API/worker secret | SUPABASE_SERVICE_ROLE_KEY | Restricted worker/admin functions only |
| API | AUTH_ISSUER, AUTH_AUDIENCE | Validate signed user tokens |
| API | GEMINI_API_KEY, GEMINI_MODEL_ID | Hosted baseline/extraction configuration |
| API | ENGINE_MODE | hosted_baseline / encoder / qwen_adapter |
| API | MODEL_MANIFEST_URI, MODEL_MANIFEST_SHA256 | Selected immutable model definition |
| API secret | MODEL_READ_TOKEN | Optional private model artifact access |
| API | ALLOWED_ORIGINS | Exact app origins if direct cross-origin access is enabled |
| API | PUBLIC_DEMO_ONLY | true for this public prototype |
| API | ENABLE_EXPLICIT_FALLBACK | false by default |
| API | RATE_LIMITS_CONFIG | Versioned quota settings from SPECS |

Only variables explicitly prefixed for public use may appear in client code. The service-role key and model API keys never do. Credential values are supplied through secret settings, not code or the agent chat.

## Build and configuration sequence

1. Create development/staging resources within the authorized account/budget.
2. Apply additive database migrations, RLS and restricted worker functions to a test project first.
3. Enable anonymous authentication and abuse protection appropriate for a public demo [REF15].
4. Configure FastAPI and model artifact locations. Start one inference worker; prevent duplicate model copies.
5. Verify that /health/ready is false until the chosen model and dependencies are usable.
6. Build the container with locked CPU serving dependencies and a non-root user. Ensure the host's PORT is honored.
7. Configure the Vercel project to use the app directory and server-side API origin. Confirm production access allows judges to reach it without a platform-login barrier.
8. Run ownership, persistence, actual-inference and restart checks against the deployed service.
9. Seed an explicitly synthetic demo dataset through a controlled function that copies rows into the visitor's own session.
10. Verify the deployed model ID/revision against the frozen manifest; capture real screenshots and a short demo video.

The implementation agent supplies exact commands only after creating and testing the repo scaffold and deployment configuration. This document is not a claim that deployment exists.

## Model packaging

Use immutable model files and hashes. Download them from trusted controlled storage during build or startup, not on every request. Keep raw training data out of the image. Model access tokens have read-only scope.

Prefer encoder CPU serving first. Confirm that the custom multi-head architecture, tokenizer, taxonomy and normalizer load together. Benchmark one report and a small queued batch with production limits.

For a generative adapter, keep the base model and adapter revisions paired. GPU hosting is optional and separately costed. Requantization/merging requires fresh task evaluation. A functioning hosted baseline does not prove that a QLoRA adapter is deployed.

## Release checklist

- [ ] Production app loads in incognito and on a phone.
- [ ] Demo session needs no judge email registration and remains isolated.
- [ ] A new narrative produces actual inference with correct provenance.
- [ ] Reopening after refresh shows the same saved record.
- [ ] Reviewer correction survives refresh and changes reviewed aggregates.
- [ ] Batch counts, exports and dashboard totals reconcile.
- [ ] Worker restart does not lose accepted jobs or duplicate stored results.
- [ ] Quotas, schema limits and failure states work in production.
- [ ] Secrets are absent from app bundle, repository and logs.
- [ ] Selected artifacts match the recorded checksums.
- [ ] Cold start, warm latency and memory are measured on the actual host.
- [ ] A labeled prerecorded demo is available separately as backup.
- [ ] Submission PDF links open correctly and name the actual active model.

## Rollback

Retain the last working app revision and model manifest. Choose the active manifest through an admin-controlled setting. Use backward-compatible database migrations; record any irreversible migration and obtain the required authorization before applying it.

After rollback, recheck model identity, one live report and one saved review. Keep failed deployment/experiment evidence rather than overwriting it.

## Cost worksheet

| Item | What to record before committing |
|---|---|
| Training | GPU type actually assigned, measured steps/hour, runtime limit and approved cap |
| Backend | Memory/CPU tier, always-on/sleep behavior, monthly or hourly billing and intended duration |
| Frontend/database | Eligibility, quota limits, inactivity behavior and storage needs |
| Hosted model | Tokens/report, request count, retries, model price and cap |
| Optional generative serving | Warm/cold latency, GPU billing while idle, disk and data transfer |

Official pricing links are in REFERENCES. The Render pricing page did not expose a usable numeric quote in this research interface, so this pack intentionally does not invent a current price. The ₹1,000–₹2,000 training envelope in FINE_TUNING_GUIDE is a proposed cap, not a cost estimate.

Start with a bounded demo period. Stop unnecessary GPU sessions and remove optional paid resources only when authorized, after preserving needed artifacts.
