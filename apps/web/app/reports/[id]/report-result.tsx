"use client";

import type { AnalysisResult, ReportDetail } from "@sih/contracts";
import { AlertTriangle, ArrowLeft, FileSearch, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { SafeguardApiError, demoAccessToken, getReport } from "../../lib/safeguard-api";

const ruleNames: Record<string, string> = {
  bypassing_safety_controls: "Bypassing safety controls",
  confined_space: "Confined space",
  driving: "Driving",
  energy_isolation: "Energy isolation",
  hot_work: "Hot work",
  line_of_fire: "Line of fire",
  safe_mechanical_lifting: "Safe mechanical lifting",
  work_authorisation: "Work authorisation",
  working_at_height: "Working at height",
};

export function ResultContent({ detail }: { detail: ReportDetail }) {
  const stored = detail.analyses[0];
  if (!stored) {
    return (
      <div className="result-empty">
        <AlertTriangle aria-hidden="true" />
        <h1>No completed assessment yet.</h1>
        <p>The report is saved, but its model job has not produced a validated result.</p>
        <Link className="button button-primary" href="/analyze">Start another analysis</Link>
      </div>
    );
  }
  const result: AnalysisResult = stored.result;
  return (
    <>
      <section className="result-hero">
        <div>
          <Link className="back-link" href="/analyze"><ArrowLeft /> New analysis</Link>
          <span className="eyebrow">Machine proposal · review pending</span>
          <h1>{result.sif_label === "unknown" ? "Insufficient evidence" : `SIF potential: ${result.sif_label}`}</h1>
          <p>{result.summary}</p>
        </div>
        <div className={`label-orbit label-${result.sif_label}`}>
          <span>{result.sif_label}</span>
          <small>SIF proposal</small>
        </div>
      </section>

      <section className="result-grid">
        <article className="result-panel evidence-panel">
          <div className="panel-heading"><span>01</span><h2>Submitted evidence</h2></div>
          <blockquote>{detail.report.narrative}</blockquote>
          {result.evidence.length ? (
            <div className="evidence-list">
              {result.evidence.map((item) => (
                <div key={item.id}>
                  <FileSearch aria-hidden="true" />
                  <p>“{item.quote}”</p>
                  <small>{item.field} · exact match · {item.method.replaceAll("_", " ")}</small>
                </div>
              ))}
            </div>
          ) : <p className="muted-copy">No defensible exact-text evidence was returned.</p>}
        </article>

        <aside className="result-panel assessment-panel">
          <div className="panel-heading"><span>02</span><h2>Assessment</h2></div>
          <h3>Relevant rules</h3>
          <div className="tag-list">
            {result.relevant_rule_ids.length
              ? result.relevant_rule_ids.map((rule) => <span key={rule}>{ruleNames[rule]}</span>)
              : <p>None identified · {result.rules_assessment} assessment</p>}
          </div>
          <h3>Barrier observations</h3>
          {result.barriers.length ? (
            <ul className="barrier-list">
              {result.barriers.map((barrier) => (
                <li key={`${barrier.tag}-${barrier.state}`}>
                  <span>{barrier.tag.replaceAll("_", " ")}</span><strong>{barrier.state}</strong>
                </li>
              ))}
            </ul>
          ) : <p className="muted-copy">No supported barrier finding.</p>}
          {result.missing_information.length > 0 && (
            <>
              <h3>Missing information</h3>
              <ul className="missing-list">
                {result.missing_information.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </>
          )}
        </aside>
      </section>

      <section className="provenance-strip" aria-label="Assessment provenance">
        <div><span>Engine</span><strong>Rakshak SIF Engine</strong></div>
        <div><span>Engine version</span><strong>v1 / Evidence-grounded</strong></div>
        <div><span>Assessment spec</span><strong>{result.provenance.prompt_version}</strong></div>
        <div><span>Rubric</span><strong>{result.provenance.label_guide_version}</strong></div>
        <div><span>Inference</span><strong>{result.provenance.inference_is_live ? "Live" : "Recorded"}</strong></div>
      </section>
      <p className="result-disclaimer">Rakshak AI produces a review proposal, not a declaration that work is safe. Human review is required.</p>
    </>
  );
}

export function ReportResult({ reportId }: { reportId: string }) {
  const [detail, setDetail] = useState<ReportDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const token = await demoAccessToken();
        const report = await getReport(reportId, token);
        if (active) setDetail(report);
      } catch (problem) {
        const message = problem instanceof SafeguardApiError
          ? problem.message
          : "The saved report could not be loaded.";
        if (active) setError(message);
      }
    }
    void load();
    return () => { active = false; };
  }, [reportId]);

  if (error) {
    return (
      <section className="result-empty">
        <AlertTriangle aria-hidden="true" />
        <h1>{error}</h1>
        <p>Reports are private to the anonymous browser session that created them.</p>
        <Link className="button button-primary" href="/analyze">Return to analysis</Link>
      </section>
    );
  }
  if (!detail) {
    return <div className="loading-page" role="status"><LoaderCircle className="spinner" /> Loading saved assessment…</div>;
  }
  return <ResultContent detail={detail} />;
}
