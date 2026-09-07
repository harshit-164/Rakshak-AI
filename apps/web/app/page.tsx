import { ArrowRight, Check, FileSearch, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { ProductHeader } from "./components/product-header";

const workflow = [
  "Submit a cleared safety observation",
  "Inspect proposed severity, rules, and exact evidence",
  "Record a human review without overwriting the model output",
];

export default function Home() {
  return (
    <main>
      <ProductHeader />

      <section className="hero" id="top">
        <div className="eyebrow">Rakshak AI / Safety intelligence unit</div>
        <h1>SEE THE<br />DANGER FIRST.</h1>
        <p className="hero-copy">
          Make safety observations reviewable. Rakshak surfaces evidence, critical-control
          context, and uncertainty—then leaves the decision with your reviewer.
        </p>
        <div className="hero-actions">
          <Link className="button button-primary" href="/analyze">
            Start a review <ArrowRight size={17} />
          </Link>
          <span className="scope-note">For synthetic or cleared public reports</span>
        </div>
        <aside className="status-card" aria-label="Prototype implementation status">
          <span className="status-dot" aria-hidden="true" />
          <div>
            <strong>System online / review mode</strong>
            <p>Private session. Exact-text evidence. Human decision required.</p>
          </div>
        </aside>
      </section>

      <section className="workflow" id="workflow" aria-labelledby="workflow-title">
        <div className="section-heading">
          <span>01 / Workflow</span>
          <h2 id="workflow-title">THE REVIEWER<br />STAYS IN CONTROL.</h2>
        </div>
        <ol>
          {workflow.map((item, index) => (
            <li key={item}>
              <span className="step-number">0{index + 1}</span>
              <p>{item}</p>
              <Check aria-hidden="true" size={19} />
            </li>
          ))}
        </ol>
      </section>

      <section className="principles" id="principles" aria-labelledby="principles-title">
        <div className="section-heading section-heading-light">
          <span>02 / Built for scrutiny</span>
          <h2 id="principles-title">NO BLACK BOX.<br />NO FALSE CERTAINTY.</h2>
        </div>
        <div className="principle-grid">
          <article>
            <FileSearch aria-hidden="true" />
            <h3>Ground every finding</h3>
            <p>Proposed findings point back to verified phrases in the submitted narrative and approved references.</p>
          </article>
          <article>
            <span className="unknown-mark" aria-hidden="true">?</span>
            <h3>Keep unknown honest</h3>
            <p>Missing facts remain unknown. A provider failure is surfaced as an error, never converted into a safety label.</p>
          </article>
          <article>
            <ShieldCheck aria-hidden="true" />
            <h3>Preserve accountability</h3>
            <p>Rakshak SIF Engine proposals and reviewer decisions remain separate, versioned records.</p>
          </article>
        </div>
      </section>
    </main>
  );
}
