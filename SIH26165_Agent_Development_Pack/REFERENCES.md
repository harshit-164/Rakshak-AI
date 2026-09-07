# References and evidence provenance

Prepared 3 September 2026.

## How to use these references

S01–S30 are inherited from the supplied SIH26165_Training_Data_Sources.docx. The sourcebook assessed catalogues and access limitations; it did not audit every underlying dataset. This pack retains its 48 hyperlinks and does not upgrade their permissions or verification status. Consult DATA_PLAN before using downloaded content.

REF01–REF23 are technical/reference pages accessed during the planning work or the immediately preceding prototype discussion. Mutable documentation, account eligibility and prices must be checked at implementation time. Proposed hyperparameters, dataset sizes, quality targets and architecture are project recommendations, not published benchmark results.

The central SIH site was not directly accessible in the earlier check. REF18 is a public template copy and REF19 is another institution’s guidance. The user’s SPOC/current portal template remains authoritative.

## Technical and planning references

| ID | Reference | Relevance |
|---|---|---|
| REF01 | [GitHub Spec Kit workflow](https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md) | Staged specification, planning, tasks and consistency checks. |
| REF02 | [Google Colab FAQ](https://research.google.com/colaboratory/faq.html) | Resource variability, notebook runtime rules and account limits. |
| REF03 | [DeBERTa-v3-small model card](https://huggingface.co/microsoft/deberta-v3-small) | Model identity, architecture and license. |
| REF04 | [Qwen2.5-1.5B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Generative base candidate and license. |
| REF05 | [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization) | Quantized PEFT preparation and LoRA setup. |
| REF06 | [Transformers text classification](https://huggingface.co/docs/transformers/tasks/sequence_classification) | Underlying sequence-classification workflow. |
| REF07 | [Transformers bitsandbytes](https://huggingface.co/docs/transformers/quantization/bitsandbytes) | Low-bit loading and hardware considerations. |
| REF08 | [TRL SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) | Prompt/completion datasets and loss masking. |
| REF09 | [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html) | Grouping while attempting class-balance preservation. |
| REF10 | [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) | Why raw scores and calibrated probabilities differ. |
| REF11 | [Hugging Face Spaces overview](https://huggingface.co/docs/hub/spaces-overview) | Current creation eligibility, visibility and basic resources. |
| REF12 | [Hugging Face Spaces hardware/lifecycle](https://huggingface.co/docs/hub/spaces-gpus) | Hardware billing and inactivity sleep. |
| REF13 | [Hugging Face pricing](https://huggingface.co/pricing) | Recheck actual plan and compute price before purchase. |
| REF14 | [Render FastAPI deployment](https://render.com/docs/deploy-fastapi) | Backend hosting workflow. |
| REF15 | [Supabase anonymous sign-ins](https://supabase.com/docs/guides/auth/auth-anonymous) | Isolated authenticated guest sessions. |
| REF16 | [Next.js on Vercel](https://vercel.com/docs/frameworks/full-stack/nextjs) | Frontend deployment support. |
| REF17 | [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output) | Schema-based model output and JavaScript integration. |
| REF18 | [2026 submission template copy](https://www.slideshare.net/slideshow/comprehensive-guide-to-smart-india-hackathon-2026-idea-submission/289077585) | Secondary copy: six slides including title and PDF instruction. |
| REF19 | [BCREC SIH 2026 guidance](https://bcrec.ac.in/sih) | Institutional confirmation of six-slide section structure; not the user college. |
| REF20 | [AGENTS.md convention](https://agents.md/) | Project instructions for coding agents. |
| REF21 | [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) | Alternative container-hosting documentation. |
| REF22 | [Render pricing](https://render.com/pricing) | Live quote required; no numeric price verified in this pack. |
| REF23 | [Supabase pgvector](https://supabase.com/docs/guides/database/extensions/pgvector) | Optional future similarity retrieval in Postgres. |

## Original sourcebook links

### S01 — IOGP high-potential event reports

- [2025sh: official report and download form](https://www.iogp.org/bookstore/product/safety-performance-indicators-2025-data-high-potential-event-reports/)
- [Earlier years: safety performance catalogue](https://www.iogp.org/bookstore/product-category/data-series/safety-performance/)

### S02 — IOGP fatal and permanent-impairment reports

- [2025sf: fatal incident reports](https://www.iogp.org/bookstore/product/safety-performance-indicators-2025-data-fatal-incident-reports/)
- [2024fpi: permanent impairment reports](https://www.iogp.org/bookstore/product/safety-performance-indicators-permanent-impairment-incident-reports-2024/)

### S03 — IOGP process-safety event narratives

- [2025pfh: official report and download form](https://www.iogp.org/bookstore/product/safety-performance-indicators-process-safety-events-2025-data-tier-1-pse-fatal-incident-and-high-potential-event-reports/)
- [Earlier process-safety reports](https://www.iogp.org/bookstore/product-category/data-series/process-safety-performance/)

### S04 — OISD case studies

- [OISD: current and archived case studies](https://www.oisd.gov.in/en-in/CaseStudies)

### S05 — PNGRB incident analysis reports

- [PNGRB: ERDMP incident analysis](https://pngrb.gov.in/eng-web/erdmp-incident-analysis.html)

### S06 — DGMS technical circulars and oil-mine rules

- [DGMS: circular archive](https://www.dgms.gov.in/UserView/index?mid=1648)
- [DGMS: official rules and resources](https://www.dgms.gov.in/)

### S07 — OSHA Severe Injury Reports

- [OSHA: dashboard and current downloads](https://www.osha.gov/severe-injury-reports)
- [Bulk ZIP linked by OSHA at research time](https://www.osha.gov/sites/default/files/January2015toNovember2025.zip)

### S08 — OSHA investigation summaries

- [OSHA: investigation summaries search](https://www.osha.gov/ords/imis/accidentsearch.html)
- [OSHA: search and field help](https://www.osha.gov/help/accident-investigation)

### S09 — NIOSH and State FACE reports

- [CDC: FACE reports and archive route](https://www.cdc.gov/niosh/face/topics/index.html)

### S10 — BSEE safety alerts

- [BSEE: safety alerts archive](https://www.bsee.gov/guidance-and-regulations/guidance/safety-alerts-program)

### S11 — BSEE panel and district investigations

- [BSEE: investigations and district-report route](https://www.bsee.gov/what-we-do/incident-investigations/offshore-incident-investigations)
- [BSEE: panel report catalogue](https://www.bsee.gov/what-we-do/incident-investigations/offshore-incident-investigations/panel-investigation-reports)

### S12 — US Chemical Safety Board investigations

- [CSB: completed investigations](https://www.csb.gov/investigations/completed-investigations/)

### S13 — IMCA Safety Flashes

- [IMCA: searchable Safety Flash archive](https://www.imca-int.com/resources/safety/safety-flashes/)

### S14 — Energy Institute Toolbox

- [Toolbox: publisher description and access](https://toolbox.energyinst.org/about-toolbox)
- [Toolbox: grouped safety resources](https://toolbox.energyinst.org/webinars)

### S15 — Step Change in Safety alerts and learnings

- [Step Change: alerts, filters and archive](https://www.stepchangeinsafety.com/alerts-learnings/)

### S16 — PHMSA pipeline incident data

- [PHMSA: bulk incident files and dictionaries](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data)
- [PHMSA: flagged-file definitions](https://www.phmsa.dot.gov/data-and-statistics/pipeline/pipeline-incident-flagged-files)

### S17 — MSHA accident, injury and narrative data

- [MSHA: open-data portal](https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp)
- [MSHA: Part 50 files, narratives and handbook](https://arlweb.msha.gov/STATS/PART50/p50y2k/p50y2k.HTM)

### S18 — Industrial Safety and Health Analytics Database

- [Kaggle: original dataset card and download](https://www.kaggle.com/datasets/ihmstefanini/industrial-safety-and-health-analytics-database)

### S19 — eMARS major-accident database

- [EEA: current eMARS home](https://industry.eea.europa.eu/seveso/accidents/)
- [EEA: major-accident data interface](https://industry.eea.europa.eu/seveso/accidents/data-on-major-accidents)

### S20 — BARPI ARIA industrial-accident database

- [Official catalogue: ARIA CSV distributions and conditions](https://data.europa.eu/data/datasets/5eb95b0d74b7d58155692f9b?locale=en)
- [BARPI: official mission and database context](https://www.aria.developpement-durable.gouv.fr/the-barpi/our-missions/?lang=en)

### S21 — NOPSEMA safety alerts and bulletins

- [NOPSEMA: alerts and bulletins](https://www.nopsema.gov.au/document-hub/alerts-and-bulletins)

### S22 — Havtil investigations and audit reports

- [Havtil: investigation reports](https://www.havtil.no/en/supervision/investigation-reports/)
- [Havtil: audits and investigation search](https://www.havtil.no/en/search-audit-reports/)

### S23 — NIOSH Fatalities in Oil and Gas Extraction

- [CDC: FOG access, definitions and request route](https://www.cdc.gov/niosh/oil-gas/about/fog/index.html)

### S24 — HSE RIDDOR tables and fatality case listing

- [HSE: fatality overview and case listing](https://www.hse.gov.uk/statistics/fatals-overview.htm)
- [HSE: tables, definitions and reuse notice](https://www.hse.gov.uk/statistics/causinj/overview.htm)

### S25 — IOGP Life-Saving Rules and Start-Work Checks

- [IOGP: Rules, implementation material and Start-Work Checks](https://www.iogp.org/workstreams/safety/safety/life-savingrules/)

### S26 — IOGP FPI scenarios and reporting definitions

- [IOGP: Potential FPI scenario examples (PDF)](https://data.iogp.org/Downloads/Safety/PotentialFPIExamples.pdf)
- [IOGP: reporting scope and definitions, 2025 data](https://www.iogp.org/bookstore/product/safety-data-reporting-user-guide-scope-and-definitions-2025-data/)

### S27 — DROPS guidance, calculator and alerts

- [DROPS: resources, calculator, alerts and reuse conditions](https://www.dropsonline.org/drops-guidance-and-resources/)

### S28 — OISD standards and recommended practices

- [OISD: standards and editions](https://www.oisd.gov.in/en-in/oisd-standards-list)
- [OISD: official access/purchase conditions](https://www.oisd.gov.in/en-in/purchase-of-standards)

### S29 — Oil India sustainability and BRSR reports

- [Oil India: sustainability reports](https://www.oil-india.com/sustainability-at-oil)
- [Oil India: BRSR reports](https://www.oil-india.com/business-responsibility-sustainability-report)

### S30 — DGFASLI Standard Reference Notes

- [DGFASLI: official reference-note archive](https://dgfasli.gov.in/en/Standard-reference-notes)
- [Example: 2021 reference note (PDF)](https://dgfasli.gov.in/public/Admin/Cms/AllPdf/65154d1d4ccce9.78613200.pdf)
