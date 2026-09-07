# Product requirements: SIH26165 SIF review prototype

Version 1.0 · Owner: Harshit/team · State: proposed implementation scope

## Problem and product goal

Safety observations, near misses and incident narratives contain signals of potential serious harm. The prototype helps an HSE reviewer identify reports with SIF potential, map relevant IOGP Life-Saving Rules, and inspect recurring activities, locations and barrier failures.

A credible first release accepts a new report, produces a traceable machine assessment, lets a human correct it, and updates a dashboard from stored records. It supports prioritization of review, not a declaration that work is safe.

## Users

- **Demo visitor:** enters through a one-click isolated demo session and works with sample or cleared public reports.
- **Reviewer:** checks evidence, corrects the SIF label and rule tags, and leaves a short reason.
- **Project maintainer:** curates reference material, runs offline training/evaluation, and chooses a versioned model for deployment.

Demo visitors may review their own session's reports. Organization-wide permissions and sponsor integration are later work.

## Primary user stories

| ID | Story | Value |
|---|---|---|
| U01 | Paste a narrative and optional activity/site/date. | Assess a new observation. |
| U02 | See the proposed SIF label, relevant rules, supporting text and missing facts. | Understand and challenge the result. |
| U03 | Correct a result while retaining the initial prediction. | Preserve accountable review and future learning data. |
| U04 | Import a small CSV and see progress/errors per row. | Demonstrate batch triage. |
| U05 | Filter saved reports and inspect recurring patterns. | Direct HSE attention toward recurring exposures. |
| U06 | Export reports, predictions and latest reviews with provenance. | Make results inspectable outside the app. |
| U07 | See which model ran and the limits of its evaluation. | Assess the credibility of the prototype. |

## Release scope

**P0 / working demo:** U01–U07, English narratives, CSV ingestion, all nine rule categories, unknown/abstention behavior, persistent jobs, isolated demo sessions, a hosted-model baseline adapter, model provenance and meaningful acceptance checks.

**P1 / trained NLP:** reviewed dataset, TF-IDF baseline, fine-tuned DeBERTa SIF classifier, multi-label rule head where annotation supports it, frozen evaluation, CPU serving and model-selection evidence.

**P2 / bounded research:** 1.5B QLoRA experiment, similar-case retrieval, independently evaluated Hindi inputs, PDF/OCR ingestion. P2 must not delay a functioning P0/P1 release. QLoRA is part of the requested learning plan; promoting it to production is conditional on evidence.

Outside this release: live sensors/CCTV, autonomous incident response, individual worker scoring, fatality-probability prediction, live integration with Oil India systems, unreviewed continuous retraining and organization-wide multi-tenancy.

## Success criteria

Product success is assessed by TEST_PLAN, not by slide claims. The main golden path is submission → real inference → persisted analysis → human correction → consistent dashboard/export.

Model success is assessed by EVALUATION. A pilot with few reviewed examples is a learning experiment. “Fine-tuned” requires changed trainable parameters, saved artifacts, successful clean reload and unseen-event evaluation. A model that does not outperform its comparator remains an honestly reported experiment.

The runtime target is a warm single-report p95 analysis time at or below 15 seconds for the encoder path on the chosen host, and a responsive job-submission acknowledgement under 2 seconds under the stated pilot load. These are engineering targets to measure, not achieved values. Baseline external-LLM latency is reported separately.

## Input and UX expectations

Use a simple three-screen flow: Analyze, Reports/Review, Dashboard. Provide readable evidence highlighting, text labels alongside color, keyboard navigation, clear current model information, and distinct waiting/error/unknown states.

Start with paste and CSV. PDF parsing often introduces extraction and OCR failures; it is postponed until the narrative pipeline is tested.

Reports are stored with immutable input versions. Correcting input creates a new version and analysis. A review never overwrites an earlier model output.

## Constraints and assumptions

- Student development machine: approximately 8 GB RAM and no suitable training GPU.
- GPU training takes place in a notebook/cloud session; CPU model serving is planned separately.
- Data collection is limited by source permissions and availability of non-SIF observations.
- A safety mentor may be unavailable. The dataset card must state who actually reviewed labels.
- All budgets and external accounts are initially unconfigured.
- No fixed deadline was supplied; use milestones and shorten optional research if needed.
- Classification concerns potential severity from the observation, with actual outcome held separately.
- Dashboard rankings reflect reported cases and reporting behavior; they are not estimates of site-wide accident risk.

## Release evidence

Before calling the prototype complete, retain the deployment URL, app revision, model revision, a short real demo recording, passed acceptance checks, a dataset summary, evaluation denominators and known limitations. If training is incomplete, show the active baseline and training status explicitly.

Detailed requirements R01–R17 and authoritative contracts are in SPECS. The source basis and design decisions are in REFERENCES and DECISIONS.
