# Demo and six-slide submission plan

## The demonstration claim

“We built an experimental NLP workflow that flags SIF potential, suggests relevant Life-Saving Rules and helps a reviewer inspect recurring precursor patterns.”

After actual training, add the exact model, reviewed training count and held-out test count. Do not substitute a trained-model screenshot for a deployed model.

## 90-second demo sequence

1. Open the public app in a clean browser and enter an isolated demo session.
2. Paste a new synthetic report with credible serious exposure despite no injury.
3. Submit and show real processing, SIF result, rule tags, verified evidence and active model identity.
4. Show an ambiguous example returning unknown with missing-information questions.
5. Review/correct one result and save the reason.
6. Open the dashboard, select reviewed mode, and show the updated numerator/denominator and barrier pattern.
7. Export the results or reopen the same report after refresh.
8. End with measured test coverage and one honest limitation.

Label synthetic examples and invented demo site names. Avoid making live safety advice from a public demonstration.

## If the network or model fails

Show the actual failure state, then offer a separate recorded demonstration labeled “Recorded example.” Never replace the live response silently with a stored sample. Keep a downloadable/publicly accessible short video for judges.

## Six-slide plan

Preserve the headings and required fields of the current template supplied by the college SPOC. The 2026 template copies checked earlier in this conversation specify six slides including title and PDF submission; confirm the final applicable template before upload [REF18/REF19].

| Slide | Main evidence |
|---|---|
| 1 Title | Required SIH fields, team and one-line project purpose |
| 2 Proposed solution | Report-to-review workflow and one actual app screenshot |
| 3 Technical approach | Architecture, selected model, data path and clickable live URL/QR |
| 4 Feasibility and viability | What works, actual data/model evaluation, limitations and reviewer loop |
| 5 Impact and benefits | Dashboard screenshot showing practical review prioritization |
| 6 Research and references | A few authoritative sources plus demo video and repository links |

The slide limit comes from the template, not from a causal claim that short decks win. External links supplement a self-contained explanation; evaluators may not open them.

## Model claims ladder

| Completed evidence | Accurate wording |
|---|---|
| Prompted API only | “Domain-guided NLP prototype using a hosted language model.” |
| Actual encoder fine-tuning, reload and evaluation | “Fine-tuned DeBERTa for SIF classification on N reviewed training events; evaluated on M unseen real events.” |
| Completed QLoRA run and comparison | “Fine-tuned a Qwen 1.5B adapter with QLoRA; compared base and adapted models on the same held-out set.” |
| Own model loaded by live server | “The deployed prototype uses model X, revision Y.” |
| Limited or weak test results | “Pilot experiment; current model limitations include …” |

Fill N/M/X/Y from real manifests only. State which rule tags were trained/evaluated and which use a reference-based fallback.

## Evidence to retain

Repository revision, model manifest, training logs, adapter/checkpoint files, dataset card, split hash, evaluation report, real screenshots and video. Publication of raw data/model files depends on their rights and user authorization.

## Before exporting the PDF

Use readable text and one primary claim per slide. Include only measured metrics with denominator/date. Verify links after PDF export. Remove template instruction slides rather than treating them as extra content slides. Avoid a separate thank-you slide when it would exceed the limit.
