# Acceptance and verification plan

Check behavior, not whether a file or component merely exists. Use deterministic provider stubs for most CI tests and at least one authorized live-provider smoke run. Test evidence must identify which kind ran.

## Requirement checks

| Check | Covers | Scenario and expected evidence |
|---|---|---|
| T01 | R01 | Create two independent anonymous sessions. B cannot list, read, review, export or aggregate A's records; direct ID requests return 404. Test API and SQL/RLS paths. |
| T02 | R02 | Valid narrative persists unchanged with a hash; blank/short/over-limit input fails predictably. Revised input creates a new version. Missing site/date stays null. |
| T03 | R03 | A fresh report reaches a real configured provider, saves actual provenance and can be reopened after browser refresh. Mock mode cannot pass production readiness. |
| T04 | R04 | Insufficient facts give unknown; malformed provider response/timeout produces failed job. Neither becomes no. Explicit fallback records the actual engine. |
| T05 | R05 | Multiple rules, all assessed-negative rules and unassessed rules retain distinct meanings. Invalid/duplicated rule IDs are rejected or normalized consistently. |
| T06 | R06 | Fabricated quote and reference IDs fail validation. Repeated phrases highlight the intended occurrence. Normalization is consistent. An LLM-generated explanation is not labeled encoder attribution. |
| T07 | R07 | Correct a label; original prediction remains. Concurrent edits with the same expected version cause one 409. New narrative version does not inherit an old review. |
| T08 | R08 | CSV handles UTF-8, quoted commas/newlines, missing required narrative, invalid dates and partial row rejection. Over-limit file/row count is rejected. Progress counts reconcile. |
| T09 | R09 | Submit duplicate idempotency key: same payload returns same resource, changed payload gives 409. Kill worker after claim, after provider response and before finalization; recovery yields one stored analysis and auditable attempts. |
| T10 | R10 | Seed exact yes/no/unknown/unreviewed cases. Check density denominator, minimum sample, latest-version rules, multi-label counts, filters and ownership. |
| T11 | R11 | Export matches current filtered records and includes distinct predictions/reviews. Values beginning with =, +, -, @ or control prefixes cannot execute as spreadsheet formulas. |
| T12 | R12 | Train a small debug artifact, save and reload in a fresh CPU process. Output heads/taxonomy/normalizer agree. Missing artifact/revision/thresholds fail readiness. |
| T13 | R13 | Same event or synthetic descendant cannot cross splits. Draft/uncleared records fail eligibility. Unknown SIF and null rules do not create negative labels or loss. |
| T14 | R14 | Evaluator includes parse errors/abstentions, uses recorded split hashes, computes expected hand-checkable metrics and never tunes on test. No final-test mode without frozen manifest. |
| T15 | R15 | Keyboard use, readable labels, mobile layout, empty dataset, loading, unknown, offline/API failure and retry paths are inspected in the running app. |
| T16 | R16 | Unauthorized/expired JWT fails; unexpected request fields rejected; secrets absent from bundle/logs; quotas enforced atomically and over-limit jobs not created. |
| T17 | R17 | Incognito user follows actual deployed demo. Active model matches the manifest; playback visibly labeled; video and pitch claims match recorded evidence. |

## Dashboard arithmetic fixture

Use a clearly synthetic, isolated test dataset. Site A has 10 reviewed current-version reports: 3 yes, 5 no, 2 unknown; plus 2 unreviewed current-version reports.

Expected density is 3/8 = 0.375, review coverage is 10/12, unknown_count=2 and unreviewed_count=2. Site A is **not ranked**, because only 8 reports have definite reviewed labels and the minimum is 10. Adding two reviewed no reports makes density 3/10 and it becomes eligible. This fixture is an arithmetic test, not a dataset quality demonstration.

Changing to predicted mode uses predicted labels and displays its provisional status. Switching real/synthetic or date filters must recalculate numerator and denominator together.

## Model behavior challenge suite

Use the synthetic examples in ANNOTATION_GUIDE plus:
- explicit negation of a hazard;
- no injury despite a serious exposure;
- hazard keywords in a training discussion;
- missing energy/exposure information;
- multiple hazards and overlapping rule relevance;
- ambiguous abbreviation;
- very long narrative beyond supported tokens;
- attempted prompt injection inside the report;
- quoted but irrelevant text;
- unsupported language;
- full provider outage.

Do not demand that every legitimate real-world ambiguous case has the fixture's expected label; establish fixture labels through the rubric. Keep this suite separate from real accuracy reporting.

## Meaningful unit/integration checks

Use pytest for contracts, permissions, queue state and metrics; a small Playwright suite for the golden path; TypeScript type checking and build checks for the app. The implementation agent selects the specific tooling versions and records commands.

Mask-loss tests should verify that changing a masked target has no effect on loss, while changing an assessed target does. Split tests must operate on ancestry, not only matching row IDs. Queue tests must use a real test Postgres instance for concurrency behavior; mocks cannot establish transaction correctness.

Avoid tests that merely assert hardcoded implementation strings. No snapshot updates to hide a real behavior regression. Stop expanding testing once the task's remaining risks and release gates are covered.

## Evidence folders to create

For each completed task, store a small evidence note with actual commands, exit status and relevant output; sanitized UI screenshots for visible changes; and a failed-check note when blocked. STATUS links to these files.

For release, retain a deployment smoke report with app revision, model manifest hash, tested endpoint, test date, current plan/hardware and known limitations. A local pass is not a deployment pass.
