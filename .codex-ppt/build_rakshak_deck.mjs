import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/home/harshit/Desktop/SIH_26";
const SKILL_DIR = "/home/harshit/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations";
const TMP_DIR = path.join(workspaceDir, ".codex-ppt");
const FINAL_PPTX = path.join(workspaceDir, "output", "Rakshak_AI_SIH_2026_Submission_v2.pptx");
const RUNTIME_PYTHON = "/home/harshit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const { resolvePresentationFont, finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href,
);
const FONT = resolvePresentationFont({ fontFamily: "Noto Sans" });

const C = {
  ink: "#13201E",
  muted: "#5C6965",
  cream: "#F5EFE5",
  paper: "#FFFDF8",
  blue: "#4562BF",
  blueSoft: "#DCE4FF",
  coral: "#D95F45",
  coralSoft: "#F8DED5",
  green: "#163C35",
  lime: "#D7FF64",
  limeSoft: "#EDFFC0",
  gold: "#F1B94A",
  line: "#C9CDC7",
  white: "#FFFFFF",
};

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

const logo = await fs.readFile(path.join(TMP_DIR, "template-inspect/assets/ppt/media/image2.png"));
const appIcon = await fs.readFile(path.join(TMP_DIR, "rakshak-icon.png"));
const homeShot = await fs.readFile(path.join(TMP_DIR, "rakshak-home.png"));
const analyzeShot = await fs.readFile(path.join(TMP_DIR, "rakshak-analyze.png"));

function box(slide, left, top, width, height, fill, radius = 0, line = "none", lineWidth = 0) {
  return slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill,
    line: { fill: line, width: lineWidth },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function textBox(slide, text, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 24,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    autoFit: options.autoFit ?? "none",
    wrap: "square",
    lineSpacing: options.lineSpacing ?? 1.05,
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

function richTextBox(slide, paragraphs, left, top, width, height, options = {}) {
  const shape = textBox(slide, "", left, top, width, height, options);
  shape.text.set(paragraphs);
  return shape;
}

function smallCaps(slide, value, left, top, width, color = C.blue) {
  return textBox(slide, value.toUpperCase(), left, top, width, 24, {
    fontSize: 13,
    bold: true,
    color,
    lineSpacing: 1,
  });
}

function header(slide, title, number) {
  slide.background.fill = C.paper;
  box(slide, 0, 0, 1280, 8, C.blue);
  textBox(slide, title, 54, 25, 940, 55, { fontSize: 34, bold: true });
  slide.images.add({
    blob: logo,
    contentType: "image/png",
    alt: "Smart India Hackathon 2026 logo",
    fit: "contain",
    position: { left: 1050, top: 14, width: 190, height: 72 },
  });
  smallCaps(slide, `0${number} / SIH26165`, 54, 84, 250, C.coral);
}

function footer(slide, number) {
  box(slide, 0, 680, 1280, 40, C.blue);
  textBox(slide, "TEAM SABLE", 48, 689, 220, 20, { fontSize: 12, bold: true, color: C.white });
  textBox(slide, String(number), 1190, 689, 40, 20, { fontSize: 12, bold: true, color: C.white, align: "right" });
}

function addLinkedLabel(slide, label, url, left, top, width, fill) {
  box(slide, left, top, width, 54, fill, 12, C.ink, 1.2);
  const body = url
    ? [[
        { run: label + "  ", textStyle: { bold: true, color: C.ink, fontSize: "14pt" } },
        {
          run: url.replace(/^https?:\/\//, ""),
          textStyle: { color: C.ink, underline: "sng", fontSize: "11pt" },
          link: { uri: url, isExternal: true },
        },
      ]]
    : [[
        { run: label + "  ", textStyle: { bold: true, color: C.ink, fontSize: "14pt" } },
        { run: "ADD URL", textStyle: { color: C.muted, fontSize: "11pt" } },
      ]];
  return richTextBox(slide, body, left + 16, top + 11, width - 32, 34, { fontSize: 16, valign: "middle" });
}

function stage(slide, x, y, w, h, number, title, detail, fill) {
  const s = box(slide, x, y, w, h, fill, 14, C.ink, 1.2);
  box(slide, x + 12, y + 13, 34, 34, C.ink, 17);
  textBox(slide, String(number), x + 12, y + 19, 34, 20, { fontSize: 13, bold: true, color: C.white, align: "center" });
  textBox(slide, title, x + 58, y + 12, w - 70, 30, { fontSize: 18, bold: true });
  textBox(slide, detail, x + 18, y + 54, w - 36, h - 66, { fontSize: 13, color: C.muted, lineSpacing: 1.1 });
  return s;
}

function connect(slide, from, to) {
  slide.shapes.connect(from, to, {
    kind: "straight",
    fromSide: "right",
    toSide: "left",
    line: { style: "solid", fill: C.ink, width: 1.8 },
    tail: { type: "arrow", width: "sm", length: "sm" },
  });
}

// Slide 1: title
{
  const slide = presentation.slides.add();
  slide.background.fill = C.cream;
  box(slide, 0, 0, 1280, 8, C.blue);
  slide.images.add({ blob: appIcon, contentType: "image/png", alt: "Rakshak AI shield", fit: "contain", position: { left: 56, top: 38, width: 48, height: 48 } });
  textBox(slide, "RAKSHAK.AI", 116, 46, 210, 30, { fontSize: 20, bold: true });
  slide.images.add({ blob: logo, contentType: "image/png", alt: "Smart India Hackathon 2026 logo", fit: "contain", position: { left: 1025, top: 20, width: 205, height: 78 } });
  smallCaps(slide, "SMART INDIA HACKATHON 2026 / TEAM SABLE", 58, 138, 520, C.blue);
  textBox(slide, "RAKSHAK AI", 56, 170, 600, 92, { fontSize: 56, bold: true, lineSpacing: 0.95 });
  textBox(slide, "Explainable SIF intelligence from near-miss reports", 58, 266, 585, 72, { fontSize: 29, bold: true, color: C.coral, lineSpacing: 1 });
  textBox(slide, "SIH26165  ·  Software  ·  Miscellaneous", 58, 357, 560, 32, { fontSize: 17, color: C.muted });
  textBox(slide, "A reviewer-first prototype that keeps exact evidence visible and uncertainty honest.", 58, 410, 520, 74, { fontSize: 20, color: C.ink, lineSpacing: 1.15 });

  box(slide, 688, 124, 522, 352, C.ink, 20);
  slide.images.add({ blob: homeShot, contentType: "image/png", alt: "Rakshak AI prototype home screen", fit: "cover", position: { left: 700, top: 136, width: 498, height: 328 }, geometry: "roundRect", borderRadius: 14 });
  box(slide, 915, 440, 245, 46, C.lime, 10, C.ink, 1.2);
  textBox(slide, "WORKING PROTOTYPE", 931, 453, 213, 20, { fontSize: 13, bold: true, align: "center" });

  addLinkedLabel(slide, "LIVE DEMO", null, 58, 555, 300, C.limeSoft);
  addLinkedLabel(slide, "VIDEO GUIDE", null, 374, 555, 300, C.coralSoft);
  addLinkedLabel(slide, "GITHUB", "https://github.com/harshit-164/Rakshak-AI", 690, 555, 520, C.blueSoft);
  textBox(slide, "Replace the two ADD URL fields before submission.", 58, 627, 520, 22, { fontSize: 12, color: C.muted });
  footer(slide, 1);
  slide.speakerNotes.textFrame.setText("Project source: local Rakshak AI repository and running prototype captured on 2026-09-07. GitHub: https://github.com/harshit-164/Rakshak-AI");
}

// Slide 2: product idea and judge journey
{
  const slide = presentation.slides.add();
  header(slide, "Idea and live demo", 2);
  textBox(slide, "One report becomes a traceable review proposal", 54, 116, 660, 40, { fontSize: 25, bold: true, color: C.blue });

  const a = stage(slide, 54, 178, 205, 144, 1, "Submit", "Paste a synthetic or cleared observation. Original text remains unchanged.", C.cream);
  const b = stage(slide, 282, 178, 205, 144, 2, "Analyze", "The engine proposes SIF potential, precursor tags, barriers, and rule context.", C.blueSoft);
  const c = stage(slide, 510, 178, 205, 144, 3, "Verify", "Every evidence quote must exist in the submitted text before the result is saved.", C.limeSoft);
  connect(slide, a, b);
  connect(slide, b, c);

  smallCaps(slide, "WHAT THE JUDGE CAN CHECK", 54, 354, 420, C.coral);
  const checks = [
    ["Three-state result", "yes, no, or unknown"],
    ["Evidence trail", "exact phrases from the report"],
    ["Human boundary", "proposal separated from final decision"],
  ];
  checks.forEach(([title, detail], i) => {
    const y = 388 + i * 70;
    box(slide, 54, y, 26, 26, i === 1 ? C.coral : C.blue, 13);
    textBox(slide, "✓", 54, y + 3, 26, 18, { fontSize: 14, bold: true, color: C.white, align: "center" });
    textBox(slide, title, 94, y - 2, 230, 26, { fontSize: 17, bold: true });
    textBox(slide, detail, 94, y + 26, 500, 24, { fontSize: 14, color: C.muted });
  });

  box(slide, 760, 124, 460, 446, C.ink, 18);
  slide.images.add({ blob: analyzeShot, contentType: "image/png", alt: "Rakshak AI analysis form", fit: "cover", position: { left: 772, top: 136, width: 436, height: 422 }, geometry: "roundRect", borderRadius: 12, crop: { left: 0, top: 0.03, right: 0, bottom: 0.06 } });
  box(slide, 814, 533, 350, 54, C.coral, 10, C.ink, 1.2);
  textBox(slide, "LIVE DEMO LINK  ·  ADD URL", 830, 550, 318, 20, { fontSize: 14, bold: true, color: C.white, align: "center" });
  textBox(slide, "2-minute path: paste → analyze → inspect evidence", 760, 607, 460, 25, { fontSize: 14, color: C.muted, align: "center" });
  footer(slide, 2);
  slide.speakerNotes.textFrame.setText("Implementation evidence: apps/web/app/analyze/analyze-form.tsx; services/api/app/validation.py; services/api/app/contracts.py. Prototype screenshot captured from the local app on 2026-09-07.");
}

// Slide 3: architecture
{
  const slide = presentation.slides.add();
  header(slide, "Technical architecture", 3);
  textBox(slide, "The interface stays stable while the model layer can change", 54, 116, 900, 36, { fontSize: 24, bold: true, color: C.blue });

  smallCaps(slide, "REVIEWER EXPERIENCE", 54, 167, 220, C.green);
  const ui = stage(slide, 54, 198, 235, 116, "A", "Next.js client", "Anonymous session, report entry, job status, result view", C.cream);
  const api = stage(slide, 322, 198, 235, 116, "B", "FastAPI service", "Auth checks, idempotency, quotas, orchestration", C.blueSoft);
  const db = stage(slide, 590, 198, 235, 116, "C", "Supabase", "Postgres, row-level security, durable queue", C.limeSoft);
  const worker = stage(slide, 858, 198, 235, 116, "D", "Analysis worker", "Leases, retries, provider adapter, provenance", C.coralSoft);
  connect(slide, ui, api);
  connect(slide, api, db);
  connect(slide, db, worker);

  const human = box(slide, 1120, 198, 100, 116, C.green, 16);
  textBox(slide, "HUMAN\nREVIEW", 1132, 225, 76, 58, { fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle" });
  connect(slide, worker, human);

  box(slide, 54, 350, 1166, 2, C.line);
  smallCaps(slide, "RAKSHAK SIF ENGINE", 54, 374, 300, C.coral);

  const baseline = box(slide, 54, 409, 535, 169, C.ink, 18);
  textBox(slide, "PROTOTYPE NOW", 76, 429, 220, 24, { fontSize: 14, bold: true, color: C.lime });
  textBox(slide, "Gemini hosted baseline", 76, 463, 360, 36, { fontSize: 25, bold: true, color: C.white });
  textBox(slide, "Versioned rubric + strict JSON contract\nExact-text evidence and reference checks\nProvider identity retained in backend provenance", 76, 512, 468, 58, { fontSize: 14, color: "#D9E4E0", lineSpacing: 1.15 });

  const next = box(slide, 623, 409, 597, 169, C.blueSoft, 18, C.blue, 1.2);
  textBox(slide, "AFTER SELECTION", 647, 429, 220, 24, { fontSize: 14, bold: true, color: C.coral });
  textBox(slide, "Train, compare, then replace the adapter", 647, 463, 520, 34, { fontSize: 23, bold: true });
  textBox(slide, "DeBERTa-v3-small for classification\nQwen 2.5 1.5B with QLoRA for structured generation\nFrozen test set, threshold review, model card, CPU reload check", 647, 508, 535, 66, { fontSize: 14, color: C.muted, lineSpacing: 1.15 });
  slide.shapes.connect(baseline, next, { kind: "straight", fromSide: "right", toSide: "left", line: { style: "dashed", fill: C.coral, width: 2 }, tail: { type: "arrow", width: "med", length: "med" } });

  textBox(slide, "Swap the model adapter only after evaluation. The UI, API, storage, and evidence checks remain.", 54, 612, 1166, 32, { fontSize: 16, bold: true, color: C.green, align: "center" });
  footer(slide, 3);
  slide.speakerNotes.textFrame.setText("Architecture evidence: README.md; apps/web/app/lib/safeguard-api.ts; services/api/app/routes.py; services/api/app/worker.py; services/api/app/validation.py; supabase/migrations. Model roadmap reflects the user's stated plan and is not presented as completed training.");
}

// Slide 4: feasibility
{
  const slide = presentation.slides.add();
  header(slide, "Feasibility and risk control", 4);
  textBox(slide, "The prototype already proves the workflow. The remaining risk sits in data quality and evaluation.", 54, 116, 1120, 52, { fontSize: 23, bold: true, color: C.blue });

  const columns = [
    {
      x: 54, fill: C.limeSoft, head: C.green, title: "PROVEN IN PROTOTYPE",
      rows: [
        ["Owner isolation", "Anonymous JWT + row-level security"],
        ["Durable processing", "Postgres queue with worker leases"],
        ["Grounded output", "Unsupported evidence quotes are rejected"],
        ["Safe retries", "Idempotency keys protect duplicate requests"],
      ],
    },
    {
      x: 450, fill: C.coralSoft, head: C.coral, title: "MAIN RISKS",
      rows: [
        ["Limited labels", "SIF precursor data needs expert review"],
        ["Domain language", "Abbreviations and site terms vary"],
        ["Alert fatigue", "Too many false positives reduce trust"],
        ["Sensitive reports", "Industrial incident text may be restricted"],
      ],
    },
    {
      x: 846, fill: C.blueSoft, head: C.blue, title: "CONTROL PLAN",
      rows: [
        ["Rights register", "Train only on cleared sources"],
        ["Two-model benchmark", "Compare classifier and small LLM"],
        ["Human thresholding", "Tune for review workload and recall"],
        ["Audit trail", "Keep model, prompt, rubric, and input hashes"],
      ],
    },
  ];
  columns.forEach((col) => {
    box(slide, col.x, 188, 350, 394, col.fill, 14, col.head, 1.2);
    box(slide, col.x, 188, 350, 58, col.head, 14);
    textBox(slide, col.title, col.x + 18, 207, 314, 22, { fontSize: 15, bold: true, color: C.white, align: "center" });
    col.rows.forEach(([label, detail], i) => {
      const y = 270 + i * 74;
      textBox(slide, label, col.x + 22, y, 306, 25, { fontSize: 17, bold: true });
      textBox(slide, detail, col.x + 22, y + 28, 306, 38, { fontSize: 13, color: C.muted, lineSpacing: 1.08 });
      if (i < col.rows.length - 1) box(slide, col.x + 22, y + 65, 306, 1, "#FFFFFF");
    });
  });
  box(slide, 54, 609, 1142, 40, C.ink, 10);
  textBox(slide, "Prototype limit: use only synthetic or cleared public reports until the data-rights review is complete.", 72, 619, 1106, 20, { fontSize: 15, bold: true, color: C.white, align: "center" });
  footer(slide, 4);
  slide.speakerNotes.textFrame.setText("Implementation evidence: services/api/app/worker.py; services/api/app/validation.py; services/api/app/persistence.py; supabase/migrations; configs/references/source-register.v1.json. No production-readiness claim is made.");
}

// Slide 5: impact and evaluation
{
  const slide = presentation.slides.add();
  header(slide, "Impact and evaluation", 5);
  textBox(slide, "Better prioritization must be demonstrated with reviewer data", 54, 116, 970, 42, { fontSize: 24, bold: true, color: C.blue });

  const chainData = [
    ["01", "Near-miss text", C.cream],
    ["02", "SIF proposal", C.blueSoft],
    ["03", "Verified evidence", C.limeSoft],
    ["04", "Reviewer action", C.coralSoft],
    ["05", "Learning loop", C.cream],
  ];
  const chainShapes = chainData.map(([n, label, fill], i) => {
    const x = 54 + i * 232;
    const s = box(slide, x, 184, 196, 88, fill, 14, C.ink, 1.1);
    textBox(slide, n, x + 14, 198, 38, 22, { fontSize: 14, bold: true, color: C.coral });
    textBox(slide, label, x + 14, 228, 168, 28, { fontSize: 17, bold: true });
    return s;
  });
  for (let i = 0; i < chainShapes.length - 1; i++) connect(slide, chainShapes[i], chainShapes[i + 1]);

  smallCaps(slide, "EVALUATION SCORECARD", 54, 314, 330, C.coral);
  const metrics = [
    ["SIF recall", "Of expert-confirmed SIF precursors, how many did the system flag?", "Safety coverage"],
    ["Evidence precision", "What share of surfaced evidence supports the proposed finding?", "Explainability"],
    ["False alert rate", "How often does the system flag a non-SIF report?", "Reviewer trust"],
    ["Median review time", "Minutes from opening a report to a recorded human decision", "Operational value"],
  ];
  metrics.forEach(([metric, definition, outcome], i) => {
    const y = 350 + i * 62;
    box(slide, 54, y, 1142, 50, i % 2 ? C.paper : C.cream, 8, C.line, 0.8);
    textBox(slide, metric, 72, y + 13, 210, 22, { fontSize: 16, bold: true, color: C.blue });
    textBox(slide, definition, 305, y + 11, 620, 28, { fontSize: 14, color: C.ink });
    textBox(slide, outcome, 960, y + 13, 210, 22, { fontSize: 14, bold: true, color: C.green, align: "right" });
  });
  textBox(slide, "No impact percentage is claimed yet. Baseline and target values will be set with OIL reviewers after pilot data is available.", 54, 617, 1142, 30, { fontSize: 14, color: C.muted, align: "center" });
  footer(slide, 5);
  slide.speakerNotes.textFrame.setText("The scorecard defines proposed evaluation metrics. No measured impact results are available in the repository as of 2026-09-07.");
}

// Slide 6: roadmap and sources
{
  const slide = presentation.slides.add();
  header(slide, "Research, roadmap, and submission links", 6);

  smallCaps(slide, "MODEL ROADMAP", 54, 121, 260, C.coral);
  const phases = [
    ["NOW", "Hosted baseline", "Complete demo flow and collect structured reviewer feedback", C.limeSoft],
    ["NEXT", "Curated labels", "Resolve data rights, define splits, annotate with domain experts", C.coralSoft],
    ["THEN", "Model benchmark", "Compare DeBERTa classifier and Qwen 2.5 1.5B QLoRA", C.blueSoft],
    ["GATE", "Safe replacement", "Promote only after held-out evaluation and model documentation", C.cream],
  ];
  phases.forEach(([tag, title, body, fill], i) => {
    const y = 156 + i * 88;
    box(slide, 54, y, 530, 72, fill, 12, C.ink, 1);
    textBox(slide, tag, 70, y + 15, 68, 18, { fontSize: 13, bold: true, color: C.coral });
    textBox(slide, title, 150, y + 10, 190, 24, { fontSize: 17, bold: true });
    textBox(slide, body, 150, y + 37, 410, 28, { fontSize: 13, color: C.muted });
  });

  smallCaps(slide, "PRIMARY REFERENCES", 638, 121, 280, C.green);
  const refs = [
    ["SafeOCS", "Near-miss and offshore precursor data program", "https://www.bts.gov/browse-statistical-products-and-data/precursor-safety-data-program/offshore-energy-safety-data"],
    ["IOGP", "Process safety indicators and Life-Saving Rules", "https://www.iogp.org/workstreams/safety/safety/life-savingrules/"],
    ["Baker et al.", "Learning injury precursors from raw reports", "https://arxiv.org/abs/1907.11769"],
    ["Petrobras 3W", "Public benchmark for undesirable oil-well events", "https://github.com/petrobras/3W"],
  ];
  refs.forEach(([title, detail, url], i) => {
    const y = 158 + i * 78;
    const t = richTextBox(slide, [[
      { run: title, textStyle: { bold: true, color: C.blue, fontSize: "16pt", underline: "sng" }, link: { uri: url, isExternal: true } },
    ]], 638, y, 205, 26, { fontSize: 16 });
    textBox(slide, detail, 638, y + 30, 520, 34, { fontSize: 13, color: C.muted });
  });

  box(slide, 638, 489, 558, 2, C.line);
  smallCaps(slide, "ADD BEFORE UPLOAD", 638, 512, 270, C.coral);
  addLinkedLabel(slide, "LIVE DEMO", null, 638, 545, 270, C.limeSoft);
  addLinkedLabel(slide, "VIDEO GUIDE", null, 926, 545, 270, C.coralSoft);
  richTextBox(slide, [[
    { run: "GitHub  ", textStyle: { bold: true, color: C.ink, fontSize: "13pt" } },
    { run: "github.com/harshit-164/Rakshak-AI", textStyle: { color: C.blue, underline: "sng", fontSize: "12pt" }, link: { uri: "https://github.com/harshit-164/Rakshak-AI", isExternal: true } },
  ]], 638, 619, 558, 24, { fontSize: 14 });
  footer(slide, 6);
  slide.speakerNotes.textFrame.setText([
    "Sources accessed 2026-09-07:",
    "SafeOCS: https://www.bts.gov/browse-statistical-products-and-data/precursor-safety-data-program/offshore-energy-safety-data",
    "IOGP Life-Saving Rules: https://www.iogp.org/workstreams/safety/safety/life-savingrules/",
    "Automatically Learning Construction Injury Precursors from Text: https://arxiv.org/abs/1907.11769",
    "Petrobras 3W: https://github.com/petrobras/3W",
    "Internal rights register: configs/references/source-register.v1.json",
  ].join("\n"));
}

await fs.mkdir(path.join(workspaceDir, ".codex-finalizer"), { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
const candidatePath = path.join(workspaceDir, ".codex-finalizer", "rakshak-candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const requirements = {
  explicitTotalSlideCount: 6,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const fontPolicy = { basis: "design", families: [FONT] };
const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(workspaceDir, ".codex-finalizer", "Rakshak_AI_SIH_2026_Submission_v2.pptx.validation.json"),
});
console.log(JSON.stringify({ final: FINAL_PPTX, result }, null, 2));
