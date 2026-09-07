# TSK02 evidence — shared schemas and fixtures

Date: 3 September 2026 (Asia/Kolkata)

Requirements: R02, R05, R06. Acceptance scope: T02/T05/T06 contract behavior only.

## Verified behavior

- Report input rejects blank/short narratives and client-supplied ownership while preserving
  the submitted narrative string unchanged.
- Model output supports multiple rules, no relevant rules, partial assessment, and the full
  unknown/unassessed state without collapsing those meanings.
- Invalid and duplicate rule IDs, placeholder provenance, missing evidence IDs, fabricated
  quotes, and non-allowlisted passage IDs fail validation.
- FastAPI OpenAPI definitions generate TypeScript types; regeneration is deterministic.

## Commands and results

```text
ruff check services/api                                    PASS
mypy services/api/app                                      PASS — 0 issues
pytest services/api/tests                                  PASS — 12 tests
npm run contracts:generate                                 PASS
sha256sum -c /tmp/contracts-before.sha                     PASS — both generated files match
npm run typecheck                                          PASS
```

All model examples in this task are synthetic fixtures. No hosted-provider call was made.
