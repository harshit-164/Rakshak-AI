import { ProductHeader } from "../components/product-header";
import { AnalyzeForm } from "./analyze-form";

export default function AnalyzePage() {
  return (
    <main className="app-shell">
      <ProductHeader compact />
      <section className="workspace-heading">
        <div>
          <span className="eyebrow">New assessment</span>
          <h1>Review an observation.</h1>
        </div>
        <p>
          Submit only synthetic or cleared public text. The assistant proposes a traceable
          assessment; it does not determine whether work is safe.
        </p>
      </section>
      <AnalyzeForm />
    </main>
  );
}
