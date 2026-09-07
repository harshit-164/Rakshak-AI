"use client";

import type { AnalysisResult, ReportDetail } from "@sih/contracts";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  CircleHelp,
  FileSearch,
  LoaderCircle,
  ShieldAlert,
} from "lucide-react";
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
  const labelMeta = {
    yes: {
      title: "Potential identified",
      detail: "The submitted evidence supports escalation for human review.",
      icon: ShieldAlert,
    },
    no: {
      title: "Not identified",
      detail: "The submitted evidence does not currently support a SIF classification.",
      icon: CheckCircle2,
    },
    unknown: {
      title: "Evidence incomplete",
      detail: "The available evidence is not sufficient for a defensible classification.",
      icon: CircleHelp,
    },
  }[result.sif_label];
  const LabelIcon = labelMeta.icon;

  return (
    <>
      <section className="result-hero">
        <div className="result-hero-copy">
          <div className="result-hero-nav">
            <Link className="back-link" href="/analyze"><ArrowLeft /> New analysis</Link>
            <span className="review-pill">Machine proposal · review pending</span>
          </div>
          <h1>{result.sif_label === "unknown" ? "Insufficient evidence" : `SIF potential: ${result.sif_label}`}</h1>
          <p>{result.summary}</p>
        </div>
        <aside className={`result-verdict label-${result.sif_label}`} aria-label={`SIF proposal: ${result.sif_label}`}>
          <div className="result-verdict-heading">
            <span>Assessment signal</span>
            <LabelIcon aria-hidden="true" />
          </div>
          <strong>{result.sif_label}</strong>
          <h2>{labelMeta.title}</h2>
          <p>{labelMeta.detail}</p>
          <div className="review-required"><span aria-hidden="true" /> Human review required</div>
        </aside>
      </section>

      <section className="result-grid">
        <article className="result-panel evidence-panel">
          <div className="panel-heading"><span>01</span><h2>Submitted evidence</h2></div>
          <div className="submitted-observation">
            <span>Original observation</span>
            <blockquote>{detail.report.narrative}</blockquote>
          </div>
          {result.evidence.length ? (
            <div className="evidence-list">
              {result.evidence.map((item, index) => (
                <article className="evidence-item" key={item.id}>
                  <div className="evidence-item-icon"><FileSearch aria-hidden="true" /></div>
                  <div>
                    <span className="evidence-index">Evidence {String(index + 1).padStart(2, "0")}</span>
                    <p>“{item.quote}”</p>
                    <small>{item.field} · exact match · {item.method.replaceAll("_", " ")}</small>
                  </div>
                </article>
              ))}
            </div>
          ) : <p className="muted-copy">No defensible exact-text evidence was returned.</p>}
        </article>

        <aside className="result-panel assessment-panel">
          <div className="panel-heading"><span>02</span><h2>Assessment</h2></div>
          <div className="assessment-section">
            <h3>Relevant rules</h3>
            <div className="tag-list">
              {result.relevant_rule_ids.length
                ? result.relevant_rule_ids.map((rule) => <span key={rule}>{ruleNames[rule]}</span>)
                : <p>None identified · {result.rules_assessment} assessment</p>}
            </div>
          </div>
          <div className="assessment-section">
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
          </div>
          {result.missing_information.length > 0 && (
            <div className="assessment-section missing-section">
              <h3>Missing information</h3>
              <ul className="missing-list">
                {result.missing_information.map((item, index) => (
                  <li key={item}><span>{String(index + 1).padStart(2, "0")}</span>{item}</li>
                ))}
              </ul>
            </div>
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
      <footer className="result-footer">
        <p className="result-disclaimer">Rakshak AI produces a review proposal, not a declaration that work is safe. Human review is required.</p>
        <Link className="text-link" href="/analyze">Review another observation <ArrowRight aria-hidden="true" /></Link>
      </footer>
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
