"use client";

import { AlertTriangle, ArrowRight, Check, LoaderCircle, LockKeyhole } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import {
  SafeguardApiError,
  createReport,
  demoAccessToken,
  getJob,
  isBrowserSafeSupabaseKey,
  queueAnalysis,
} from "../lib/safeguard-api";

type Phase = "idle" | "session" | "report" | "queued" | "error";

const phaseCopy: Record<Exclude<Phase, "idle" | "error">, string> = {
  session: "Starting an isolated demo session…",
  report: "Saving the report unchanged…",
  queued: "Running the evidence-grounded assessment…",
};

const configured = Boolean(
  process.env.NEXT_PUBLIC_SUPABASE_URL &&
    isBrowserSafeSupabaseKey(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY),
);

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function waitForJob(jobId: string, token: string) {
  const started = Date.now();
  let interval = 2_000;
  while (Date.now() - started < 120_000) {
    await wait(interval);
    const job = await getJob(jobId, token);
    if (job.status === "completed") return job;
    if (job.status === "failed") {
      const message =
        job.error_code === "provider_unavailable"
          ? "The Rakshak review engine could not be reached. The report is saved; try again later."
          : "The Rakshak review engine response could not be safely validated. The report remains saved.";
      throw new SafeguardApiError(message, job.error_code ?? "analysis_failed", true);
    }
    interval = Math.min(interval * 2, 10_000);
  }
  throw new SafeguardApiError(
    "The analysis is taking longer than expected. Your report is saved in this demo session.",
    "analysis_pending",
    true,
  );
}

export function AnalyzeForm() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("idle");
  const [message, setMessage] = useState("");
  const [canRetry, setCanRetry] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setCanRetry(false);
    const form = new FormData(event.currentTarget);
    const narrative = String(form.get("narrative") ?? "");
    const optional = (name: string) => {
      const value = String(form.get(name) ?? "").trim();
      return value || null;
    };

    try {
      setPhase("session");
      const token = await demoAccessToken();
      setPhase("report");
      const report = await createReport(
        {
          narrative,
          activity: optional("activity"),
          site: optional("site"),
          report_date: optional("report_date"),
          is_synthetic: form.get("is_synthetic") === "on",
        },
        token,
        crypto.randomUUID(),
      );
      window.localStorage.setItem("safeguard:last-report", report.report_id);
      setPhase("queued");
      const job = await queueAnalysis(report.report_id, token, crypto.randomUUID());
      await waitForJob(job.job_id, token);
      router.push(`/reports/${report.report_id}`);
    } catch (error) {
      const problem =
        error instanceof SafeguardApiError
          ? error
          : new SafeguardApiError("The request could not be completed.", "request_failed", true);
      setMessage(problem.message);
      setCanRetry(problem.retryable);
      setPhase("error");
    }
  }

  const busy = !["idle", "error"].includes(phase);
  return (
    <section className="analysis-workspace" aria-label="Safety observation analysis">
      <form className="observation-form" onSubmit={submit}>
        <div className="form-intro">
          <span>01 / Observation</span>
          <strong>Original text is retained exactly as submitted.</strong>
        </div>
        <label htmlFor="narrative">Observation narrative</label>
        <textarea
          id="narrative"
          name="narrative"
          minLength={20}
          maxLength={8000}
          required
          disabled={busy || !configured}
          placeholder="Describe what happened, who or what was exposed, and which controls were present or absent…"
        />
        <div className="field-grid">
          <div>
            <label htmlFor="activity">Activity <span>optional</span></label>
            <input id="activity" name="activity" maxLength={120} disabled={busy || !configured} />
          </div>
          <div>
            <label htmlFor="site">Site <span>optional · not sent to model</span></label>
            <input id="site" name="site" maxLength={120} disabled={busy || !configured} />
          </div>
          <div>
            <label htmlFor="report_date">Report date <span>optional · not sent to model</span></label>
            <input id="report_date" name="report_date" type="date" disabled={busy || !configured} />
          </div>
        </div>
        <label className="check-field">
          <input name="is_synthetic" type="checkbox" defaultChecked disabled={busy || !configured} />
          <span>
            <strong>This is synthetic demo content</strong>
            Do not submit confidential, personal, or internal incident data.
          </span>
        </label>
        <button className="submit-analysis" type="submit" disabled={busy || !configured}>
          {busy ? <LoaderCircle className="spinner" aria-hidden="true" /> : <ArrowRight aria-hidden="true" />}
          {busy ? "Assessment in progress" : "Analyze observation"}
        </button>
      </form>

      <aside className="analysis-side" aria-live="polite">
        {!configured ? (
          <div className="setup-state">
            <LockKeyhole aria-hidden="true" />
            <span>Configuration required</span>
            <h2>Connect Supabase to begin.</h2>
            <p>
              Add the two public Supabase variables, API service credentials, and a server-only
              server-only analysis credentials. No secret belongs in the browser bundle.
            </p>
            <code>cp apps/web/.env.example apps/web/.env.local</code>
          </div>
        ) : phase === "error" ? (
          <div className="error-state" role="alert">
            <AlertTriangle aria-hidden="true" />
            <span>Assessment interrupted</span>
            <h2>{message}</h2>
            <p>{canRetry ? "You can safely submit again; idempotency protects exact retries." : "Check the deployment configuration before retrying."}</p>
          </div>
        ) : busy ? (
          <div className="progress-state">
            <LoaderCircle className="spinner" aria-hidden="true" />
            <span>Live workflow</span>
            <h2>{phaseCopy[phase as keyof typeof phaseCopy]}</h2>
            <ol>
              <li className="done"><Check /> Isolated session</li>
              <li className={phase === "report" || phase === "queued" ? "done" : ""}><Check /> Persisted report</li>
              <li className={phase === "queued" ? "active" : ""}><LoaderCircle /> Rakshak assessment</li>
            </ol>
          </div>
        ) : (
          <div className="idle-state">
            <span>02 / What returns</span>
            <h2>A proposal you can inspect, not a verdict.</h2>
            <ul>
              <li>Yes, no, or honestly unknown SIF potential</li>
              <li>Relevant Life-Saving Rules with assessed coverage</li>
              <li>Exact-text evidence and barrier observations</li>
              <li>Visible assessment version and rubric provenance</li>
            </ul>
          </div>
        )}
      </aside>
    </section>
  );
}
