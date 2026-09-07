# Data acquisition, eligibility and lineage

## What the supplied document gives you

The sourcebook is a research catalogue. It has not delivered labeled training rows, audited every download or established blanket ML reuse rights. Retain its identifiers S01–S30; REFERENCES preserves every original hyperlink.

Create a source register before collecting. Suggested fields: source_id, URL, title, publisher, version/date, downloaded_at, document_sha256, access_method, training_permission_status, permission_basis, redistribution_status, original_label_system, extraction_status, reviewer and notes.

Permission status is cleared / unresolved / restricted. Keep the actual basis; public availability alone does not make a record cleared. A record can be eligible for internal experimentation while not eligible for redistribution, but document the permission for that intended use. No personal names/emails/employee identifiers are necessary in the corpus.

## Acquisition priorities

| Priority | Sourcebook entries | Intended use | Limitation to retain |
|---|---|---|---|
| 1 | S25 IOGP Rules; S26 FPI guidance | Taxonomy and annotation rubric | Guidance is not a real incident dataset. |
| 1 | S01–S03 IOGP narratives | Positive mechanisms and oil/gas vocabulary | Serious-event bias; form access and reuse need checking. |
| 1 | S13 IMCA | Short narratives and source rule tags | Tags indicate relevance, not proven breaches; review reuse. |
| 1 | S04 OISD; S05 PNGRB | Indian petroleum cases | Sourcebook could not verify individual downloads. |
| 1 | Sponsor/college safety partner | Comparable minor incidents, observations and non-SIF cases | Availability and permission unknown; human request only. |
| 2 | S07 OSHA; S08 investigations; S09 FACE | Public narrative extraction and hazard coverage | No ready SIF target; severe/fatal selection bias. |
| 2 | S10–S12 BSEE/CSB | More offshore/process examples | Cross-publication duplicates and outcome leakage. |
| 2 | S18 Kaggle industrial safety | Learn preprocessing and establish a community-data benchmark | Inspect actual license/provenance; potential levels are not automatically SIF labels. |
| Later | S14–S17, S19–S24, S27 | Coverage gaps | Retain geographic/domain and source restrictions. |
| Context | S06, S28–S30 | Terminology, standards and project context | Do not expand statistics or guidelines into fake observed events. |

Begin with sources you can actually access and use lawfully. If a PDF needs a form, Harshit downloads it through the normal route; the agent can parse the supplied file. Do not bypass sign-in, paywalls or access limits.

## Staged dataset targets

These are project planning targets, not scientific sufficiency thresholds.

| Stage | Approximate real reviewed events | Use |
|---|---:|---|
| Seed | 30–50 | Agree on labels and test extraction. |
| Pilot | 200–400 | Compare basic models and reveal dataset problems. |
| Expanded pilot | 500–1,000 | More credible held-out comparisons and hazard coverage. |

A useful example allocation at 600 distinct reviewed events is approximately 400 train / 100 validation / 100 final test, keeping event groups intact. Group constraints and label coverage take precedence over exact row counts. If only 300 events exist, use a smaller held-out pilot and disclose the limits; do not manufacture extra “real” cases.

Track yes/no/unknown counts and per-rule positives at each stage. Both definite SIF classes must be represented in training and evaluation. Seek source overlap across labels: if every positive comes from fatal-investigation reports and every negative from synthetic office examples, the task is confounded.

The hardest acquisition task is comparable non-SIF observations. An observed minor injury or absence of injury is not sufficient for a negative label. Use ANNOTATION_GUIDE.

## Event processing pipeline

1. Download through supported access and record provenance/rights.
2. Extract text and retain page/section pointers to the original file.
3. Separate the initial observation narrative from source label, actual outcome, investigation conclusions and recommendations.
4. Redact identifiers, without deleting task/exposure/control facts.
5. Normalize whitespace/Unicode consistently; retain original text in controlled storage.
6. Find duplicates by source event ID, normalized text hash and manual review of dates/locations/equipment/events. Similarity search proposes duplicates; it does not settle identity.
7. Assign a stable event_group_id shared by all versions, publishers, translations and paraphrases.
8. Two team annotators independently label a seed; adjudicate disagreements, preferably with a safety mentor.
9. Record label status and annotation masks. Export only eligible reviewed examples.
10. Split groups before augmentation; freeze the split manifest and test-pool hash.

If post-event analysis is needed to understand a case, keep it available to the annotator but not as a model input. The label must be supportable from the chosen observation view. If the chosen view lacks necessary facts, use unknown even if the complete investigation reveals serious harm.

## Canonical offline training row

Fields below are required unless explicitly nullable:

- record_id, event_group_id, source_id, source_url (nullable for genuine synthetic records), document_sha256, page_or_section
- input.narrative, input.activity (nullable), normalization_version, input_sha256
- context.site, context.report_date, source_outcome, original_source_label (nullable, audit only)
- targets.sif_label: yes / no / unknown
- targets.rule_values: nine entries of 0 / 1 / null in the SPECS order
- targets.confirmed_breach_ids: reviewer-established IDs, separate from rule_values
- targets.evidence: verified quotes and associated target IDs
- targets.precursors, targets.barriers, targets.missing_information
- annotation.status: draft / reviewed / adjudicated
- annotation.annotators, annotation.reviewer, annotation.guide_version, annotation.reviewed_at
- lineage.is_synthetic, lineage.parent_event_group_ids, lineage.generator_model (nullable), lineage.transformation, lineage.language
- eligibility.training_permission_status, eligibility.permission_basis, eligibility.redistribution_status
- split: train / validation / test / quarantine

A null rule target means unassessed, not absence. Missing narrative, unknown rights, unresolved duplicate group or draft annotation sends a record to quarantine. Unknown SIF with reviewed rule targets may contribute only to the rule loss; it does not contribute a negative SIF target.

## Synthetic data policy

Use 10–50 small synthetic fixtures to test the UI and output schema. That is not enough evidence for useful generalization.

For augmentation, start with at most one reviewed variant per eligible training event and compare against a real-only training run. This cap is an initial experimental choice. Any synthetic variant inherits its parent's training-only status. A composite scenario inherits all parent groups; if any parent belongs to validation/test, it cannot be used for training.

Change causally relevant facts only with label re-review. Merely inserting “no injury” does not turn yes into no. Vary phrasing, abbreviations and incomplete descriptions. Record the generator and prompt version, check applicable provider terms, and never invent official source IDs/URLs.

Validation and final test use real reviewed events only. Keep a separate synthetic challenge suite for behavioral checks and label its results accordingly.

## Dataset card to produce before training

Write a DATASET_CARD for the actual dataset with:
- actual counts of unique events, rows, sources, years, domains and labels;
- class and rule counts for each split;
- extraction/rights/PII handling;
- annotator qualifications, agreement sample and adjudication process;
- eligibility exclusions and duplicate checks;
- actual-input-view rules and examples of removed outcome leakage;
- synthetic count and lineage;
- remaining gaps, especially representative non-SIF and Indian/sponsor records.

If no sponsor records were obtained, say so. Demo site names may be synthetic, but must not be presented as real Oil India site statistics.
