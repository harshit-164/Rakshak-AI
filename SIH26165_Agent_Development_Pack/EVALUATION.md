# Evaluation and model selection

No metrics in this pack are measured results. Targets below are proposed pilot gates; they do not establish suitability for operational safety decisions.

## Questions to answer

1. Does the model identify SIF-potential reports better than a simple text baseline?
2. How often does it miss SIF cases, raise false flags or abstain?
3. Are rule tags useful across all assessed rules, including rare ones?
4. Do explanations quote real input facts and valid reference passages?
5. Does the deployed artifact reproduce the offline model within tolerance?
6. Can it run reliably within the chosen deployment's memory and latency budget?

## Datasets and freeze rules

Group by underlying event before splitting. Group assignment applies to source copies, chunks, translations and all synthetic descendants. Use group-aware stratification when feasible; scikit-learn documents StratifiedGroupKFold [REF09]. A stratification algorithm cannot create missing class/source coverage.

Keep:
- training pool for weights, vocabulary and eligible retrieval examples;
- validation pool for model choice, thresholds, calibration and early stopping;
- final real test pool for a frozen comparison;
- separate synthetic challenge suite for behavior checks;
- source/region and over-length challenge subsets when available.

Hash the final test manifest before model selection. Freeze candidate configurations and thresholds before opening final test results. If later development uses test errors, that pool becomes development data; reserve new events for the next final test.

Use identical observation views for fair comparisons. If the encoder supports only shorter reports, show both performance on the shared supported subset and coverage/performance of the full deployed policy. Do not compare an encoder's filtered easy subset with an LLM's entire dataset and call it fair.

## Model runs

| Run | Description |
|---|---|
| B0 | TF-IDF + logistic regression, trained on the same eligible train split |
| B1 | Fixed hosted prompt/reference baseline |
| E1 | Fine-tuned encoder SIF model |
| E2 | Encoder with rule head where annotation permits |
| Q0 | Untuned Qwen 1.5B with the same task prompt |
| Q1 | Qwen 1.5B plus the trained QLoRA adapter |

Run only candidates that exist. Use validation to choose a primary candidate and keep a limited predeclared comparator set for final testing. Compare E1/E2 real-only vs augmented training if synthetic data is used. No claim that Q1 improves unless the comparison supports it.

For generative runs, record provider/model version, decoding settings, prompt hash, reference bundle hash and parse failures. Invalid outputs are errors; they may not be silently removed from the evaluation denominator.

## Metrics with explicit denominators

For real examples with true yes/no labels:

- **Strict SIF recall:** true-yes predicted yes / all true-yes. Abstained positives count as not detected here.
- **SIF precision:** true-yes predicted yes / all predicted yes.
- **False-negative rate:** true-yes predicted no / all true-yes. Report abstained positives separately.
- **Review-routing recall:** true-yes predicted yes or unknown / all true-yes. Report this separately; “unknown for everything” is not a useful classifier.
- **Coverage:** definite predictions / all evaluated inputs; errors are shown separately and do not improve coverage.
- **Macro F1/balanced accuracy:** specify the treatment of abstention. The main report includes the full truth-by-prediction table, not a selective score over only answered cases.
- **Unknown handling:** among true-unknown cases, report predicted unknown, overconfident yes/no and error counts.
- **Rule micro/macro F1:** compute only on assessed target entries; list support per rule. Never turn null labels into zeros.
- **Evidence validity:** proportion of proposed quotes that actually match the supplied input.
- **Evidence support:** human-reviewed subset measuring whether matched quotes justify the associated claim.
- **Reference validity:** returned IDs exist in the approved bundle and support the stated rule context.
- **JSON validity:** parser/schema success / all attempted generative outputs, with first-pass and repaired-output rates separate.
- **Runtime:** cold start, warm p50/p95 latency, peak RSS/VRAM, request count and cost where measurable.

A syntactically matching quotation can still be irrelevant. Do not confuse substring validation with domain correctness.

Present counts with every percentage. Add uncertainty intervals where reasonable; document whether intervals are event-level Wilson intervals or a group-preserving bootstrap. Rare rules with fewer than 10 assessed positive test examples are descriptive only.

## Thresholds and score presentation

Select low/high SIF thresholds on validation, never on the final test. Tune class weights and any rule thresholds on training/validation only. Record thresholds and their model/data versions in the model manifest.

Calibration, if attempted, uses a separate calibration portion of development data or a documented cross-validation design. A raw sigmoid/softmax value is not guaranteed to be calibrated; probability calibration is a separate procedure [REF10]. Never interpret a classifier score as the probability that an accident will occur.

For unsupported rules, return a partial/unknown assessment rather than pretending the tag was conclusively absent. Store supported_rule_ids in the manifest. All nine targets must still retain their canonical order.

## Proposed encoder promotion gates

For a public student prototype, require:
1. Artifacts exist, reload correctly and pass the API/CPU checks.
2. Eligible real data and event-separated splits are documented.
3. The final pilot has at least 50 definite real events, including at least 20 yes and 20 no; smaller results are labeled a learning demonstration.
4. On validation, target strict SIF recall ≥0.90, precision ≥0.60 and coverage ≥0.70. These are initial engineering targets; they are not industry standards.
5. On the frozen final comparison, disclose whether those targets hold and compare against B0/B1. Prefer a candidate with useful recall/precision and credible coverage; do not automatically prefer the trained model.
6. No unresolved cross-user access, fabricated provenance, corrupted artifacts or systematic silent failure.
7. CPU memory fits the chosen host with headroom and measured latency is acceptable for the demo.

Even passing these gates permits only an explicitly experimental, human-reviewed demonstration. No safety effectiveness claim follows from a small selected test set.

If model quality is weak, keep the best baseline active, include the fine-tuning experiment and failure analysis in the report, and continue improving data. A completed training experiment need not become the production model.

## QLoRA experiment completion gate

An experiment is complete when trainable adapter parameters changed, persistent adapter files exist, a clean base-plus-adapter reload succeeds, and Q0/Q1 are compared on identical unseen real inputs. Report classification, tags, grounding, parsing and latency, not only loss.

Promote Q1 to serving only if it meets the same data/application requirements and offers a measured benefit over the selected alternative. Record the hardware/budget needed to keep it available.

## Evaluation report and model card fields

Each candidate must have:
- run ID/date, code revision, environment lock and seed;
- base model revision, artifact checksums and tokenizer;
- dataset/split/input-view hashes and actual counts;
- annotation/reviewer qualifications and source rights basis;
- decoding/threshold/calibration settings;
- overall and per-source/rule metrics with denominators;
- errors, abstentions, false negatives and known failure modes;
- data leakage checks and synthetic contribution;
- CPU/GPU latency/memory;
- decision: selected / experimental / rejected, with reason.

Do not store actual metrics until a run produces them. STATUS starts with “not run,” not zeros or aspirational percentages.
