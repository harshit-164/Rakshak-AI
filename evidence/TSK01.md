# TSK01 evidence — scaffold and configuration

Date: 3 September 2026 (Asia/Kolkata)

Requirements: R15, R16. Acceptance scope: project scaffold, locked dependencies, build and
configuration hygiene. This note does not claim production deployment or live inference.

## Verified behavior

- npm workspaces build the Next.js app and generated-contract package.
- The FastAPI process exposes minimal liveness and fails readiness closed while external
  dependencies are unconfigured.
- `.env.example` names browser-safe and server-only variables without containing values.
- The landing shell was inspected in a running browser at desktop and 390 px widths. Its
  semantic headings/navigation are readable, the browser console is clean, and a discovered
  narrow-screen overflow was corrected.

## Commands and results

```text
npm audit --audit-level=high        PASS — 0 vulnerabilities
npm run lint                        PASS
npm run typecheck                   PASS
npm run test                        PASS — 1 web test
npm run build                       PASS — Next.js 16.3.4 production build
ruff check services/api             PASS
mypy services/api/app               PASS — 0 issues
pytest services/api/tests           PASS — included in current 12-test suite
```

An initial audit found GHSA-5xrq-8626-4rwp through Vitest 3.2.4. The dependency was upgraded
to 3.2.7 and the audit was rerun; the passing result above is the current state.

## Boundary

Gemini and Supabase credentials were not present. `/health/ready` returning 503 is therefore
the expected secure behavior, not evidence of a deployed integration.

