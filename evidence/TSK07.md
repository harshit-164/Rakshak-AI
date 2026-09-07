# TSK07 — Deployable preview configuration evidence

State: in progress; deployable configuration exists, no cloud deployment is claimed.

Created:

- `services/api/Dockerfile`: locked uv environment, non-root runtime, one API/worker process,
  host-provided port, prompt/reference/manifest assets.
- `render.yaml`: Docker web service, liveness endpoint, one instance, safe defaults, and
  dashboard-prompted secrets (`sync: false`).
- `vercel.json`: repository-root npm-workspace Next.js build.
- `.dockerignore`: excludes secrets, local environments, raw data, notebooks, and model files.

Verification:

- Render YAML and Vercel JSON syntax parse locally.
- The Next.js production build passes from the repository root.
- Consolidated `npm run check`, Ruff, strict mypy, 29 API tests, and npm audit passed;
  npm reported zero vulnerabilities.
- Docker image execution was not tested because Docker/Podman/Buildah are unavailable in the
  current machine. Render/Vercel CLIs are also unavailable.

Acceptance not yet met:

- No account, budget, domain, secret, or deployment authorization was supplied. Live incognito,
  mobile, cold-start, memory, latency, and rollback checks remain external blockers.
