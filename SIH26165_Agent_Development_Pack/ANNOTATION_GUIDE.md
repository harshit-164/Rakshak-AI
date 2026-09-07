# Annotation guide: sif-pilot-v1

This is a proposed project rubric, grounded in sourcebook S25–S26. Obtain domain review and align it with the sponsor's definition when available. Changes require a version bump and review of affected records.

## The SIF question

Could the reported exposure realistically result in fatality or a life-altering serious injury, given the task, energy/hazard, person position and controls described?

Use realistic potential supported by the narrative. Avoid elaborate hypothetical chains with several unrelated failures. Actual injury severity is a separate field.

- **yes:** the narrative establishes a credible serious-harm mechanism and exposure or a relevant critical-control failure.
- **no:** sufficient description supports a low-potential event under this rubric.
- **unknown:** essential exposure, energy, task or safeguard facts are missing; the meaning is ambiguous; or available information does not support a defensible decision.

“No injury,” “near miss,” “minor,” and a source's category name are not decision rules. A generic rule breach is not automatically SIF. No relevant Life-Saving Rule does not mean no SIF hazard.

## Reviewer sequence

1. Identify the actual task and hazardous energy/substance.
2. Identify the exposed person and their position relative to the hazard.
3. List controls explicitly present, absent or failed; silence is unknown.
4. Describe a credible harm pathway in one short sentence.
5. Choose yes/no/unknown and quote the supporting input text.
6. Tag relevant rules independently; mark unassessed rules null.
7. Record confirmed breaches only when the input establishes them.
8. Extract activity and barrier/precursor tags with supporting text.
9. Record missing facts and disagreements.

Do not let the AI-generated draft become the default answer for both reviewers. Review at least the seed and the final evaluation cases independently before comparing drafts.

## Rule targets

Use the exact nine IDs and ordering in SPECS. Each target is 1 relevant, 0 reviewed and not relevant, or null not assessable. Multiple rules may apply; all zero is valid when assessed. No positive labels does not establish that all were reviewed.

Relevant means connected to the task/exposure/control. Confirmed breach is a narrower conclusion. For example, a report about energy isolation does not itself prove that isolation was omitted.

Barrier state meanings:
- present: stated as in place;
- failed: stated not to have performed its intended protective function;
- missing: stated as absent;
- unknown: not described well enough.

## Synthetic examples for learning and tests

These examples are invented. They are not part of a real-event evaluation set.

| Narrative | Proposed label | Rationale |
|---|---|---|
| “A suspended load passed directly above a worker during lifting. Nobody was injured.” | yes | Explicit person/load exposure can have serious consequences. Relevant: line_of_fire and safe_mechanical_lifting. |
| “An office employee received a shallow paper cut while sorting paper files at a desk. No powered equipment or other hazard was involved.” | no | Stated mechanism supports a low-potential event. No rule automatically applies. |
| “A lifting issue occurred at site A. Details unavailable.” | unknown | Exposure, load and controls are unspecified. |
| “Maintenance was planned. The report does not say whether equipment was isolated or work began.” | unknown | Lack of isolation information is not evidence of live maintenance. |
| “The report says 'hot work permit' but describes only a training discussion; no operational task or exposure is described.” | unknown | Keyword presence is insufficient to classify operational potential. |

These are proposed labels to verify with the project's reviewer. Fixtures check known behavior; they do not prove broad accuracy.

## Precursor and barrier vocabulary

Start with a controlled, extensible list, such as overhead_load_exposure, uncontrolled_energy, loss_of_containment, person_in_vehicle_path, unprotected_fall_exposure and confined_space_atmosphere_unknown.

A tag requires matching narrative evidence. Use an “other” tag with a short description when needed; curator review decides whether to extend the vocabulary. Store synonyms separately so recurring-pattern counts do not split “LOTO missing” and “isolation absent” arbitrarily.

Do not tag missing precautions solely because an investigator recommended them later. Do not infer exact location, dates, equipment specifications or mass from general knowledge.

## Agreement and adjudication

Double-label a seed of 30–50 diverse real events. Report agreement before discussion, confusion by class and examples of disagreement. Cohen's kappa may supplement raw agreement for SIF labels, but label imbalance and a small sample limit interpretation. For rule tags, report per-rule agreement over jointly assessed targets.

Adjudicate disagreements and preserve both original labels. Use reviewer notes to refine the rubric. Re-review examples affected by a changed definition; retain the old label/version in the audit trail.

Final-test annotation must be frozen before model comparison. If a genuine label error is found after testing, record the correction, invalidate affected scores and create a clearly versioned evaluation report.

## Operational interpretation

An unknown result belongs in the review queue. A no result means the pilot rubric did not establish SIF potential in the supplied narrative; it is not permission to proceed with work. The prototype makes no automatic control decisions.
