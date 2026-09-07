# TSK12 — Source register and parsing evidence

State: in progress; four records are ready for human screening, not five accepted records.

Created `configs/references/source-register.v1.json` with file hashes, page counts, retrieval
notes, and unresolved rights status. Created four quarantined draft JSONL records under
`data/draft_extractions.jsonl`, each separating source outcome from model input and leaving all
review labels null.

All 11 pages across the four supplied PDFs were rendered and visually inspected. The DOCX text
and tables were extracted and its 30-entry catalogue was reviewed; visual DOCX rendering could
not run because LibreOffice (`soffice`) is absent. None of these records is eligible for model
training until rights and human annotation are resolved.

TSK12 remains unchecked because its five-inspected-record acceptance count is not yet met and
the four candidate records have not been independently reviewed.
