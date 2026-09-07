# Decision record

Version 1.0 · proposed defaults for implementation · 3 September 2026

## D01 — Add a Python backend

Earlier recommendation: Next.js server routes with a hosted model for the fastest demo.

Updated decision: Next.js frontend plus FastAPI because the user now wants actual fine-tuning and deployment of owned model artifacts. This introduces one extra service but gives training and serving a shared Python implementation. Keep one database and one model adapter contract.

## D02 — Compact classifier is the primary training target

Fine-tune DeBERTa for SIF first; add a masked multi-label rule head. The central task is classification, so a generative LLM is not required to demonstrate an NLP engine. This path makes CPU deployment more practical to investigate.

This is a design recommendation, not a benchmark claim. If the trained classifier underperforms, keep the better baseline and report the experiment.

## D03 — QLoRA is a separate requested experiment

Use Qwen 1.5B Instruct with a bounded QLoRA run to teach the desired JSON assessment behavior. The small model and short sequence target reduce the experiment's resource ambition. Hardware fit and quality must be measured.

Do not promise a 7B model, free GPU hosting, or improved accuracy. A larger Mistral-family model remains a later comparison if a real need, data and budget emerge.

## D04 — Improve data before increasing model size

The sourcebook is dominated by serious-event sources and does not contain a ready labeled corpus. Prioritize comparable reviewed non-SIF examples, annotation quality, event deduplication and a real held-out set.

Use 30–50 events for rubric development, 200–400 for a pilot and 500–1,000 as an expansion goal. These are planning targets, not a mathematical guarantee of quality.

## D05 — Keep uncertainty and operational failure distinct

Binary encoder scores are translated through validation-chosen thresholds; insufficient input can abstain. Hosted/QLoRA outputs can return unknown. Provider failures become failed jobs. Unknown is not a negative class for encoder training.

## D06 — Preserve evidence provenance

Separate model classification, extracted evidence and human review. Quoted evidence is verified against input, and generated summaries are not presented as causal attribution of a classifier. Rule relevance and confirmed breach remain different fields.

## D07 — Use Postgres for a small durable queue

A single-process worker with a durable queue, leases and restart checks is enough for this bounded demo. Avoid Redis/Celery/Kubernetes until workload requires them. Exactly-once external model calls are not promised.

## D08 — Spec-driven work uses measurable slices

Use one implementation lead and dependency-ordered tasks. A feature is complete when its observable acceptance check passes. This pack does not require installing Spec Kit or a multi-agent runtime. Parallel coding agents are used only with appropriate live authorization.

## D09 — Public demo sessions are isolated

Use one-click anonymous authenticated sessions, owner-scoped data and explicit synthetic sample records. The demo does not require judge email registration. Shared sample data is copied into the visitor's session; reviewer edits do not affect other visitors.

## D10 — Hosting is independently budgeted

Train in Colab; serve the encoder on a measured CPU host. Default deployment is Vercel + Render + Supabase. Current Hugging Face compute-Space eligibility differs from older free-hosting tutorials, so it is an alternative only after checking current access/pricing.

## D11 — Defer PDF/OCR and large retrieval infrastructure

Paste/CSV prove the core task with fewer extraction failure modes. A small versioned rule bundle is sufficient initially; pgvector can be added when reference selection adds measurable value.

## D12 — Claims follow saved evidence

“Fine-tuned NLP engine” requires changed weights, saved artifacts, clean reload and held-out evaluation. “Fine-tuned LLM” additionally requires a completed generative adapter/weight update. “Deployed” requires a live endpoint running that model. All remain experimental unless appropriate real-world validation later establishes more.

## Open decisions and defaults

| Decision | Default until user/sponsor provides more |
|---|---|
| Actual submission date | No fixed date assumed; milestone schedule |
| Training budget | No spend authorized; suggested optional cap in FINE_TUNING_GUIDE |
| Serving budget | No spend authorized; quote after profiling |
| HSE reviewer | None confirmed; team-reviewed labels disclosed |
| Sponsor data availability | Unconfirmed; public/cleared sources only |
| Language scope | English; unsupported language abstains |
| SIF definition | sif-pilot-v1 pending sponsor/domain alignment |
| Public model/data release | No automatic publication; check rights first |
