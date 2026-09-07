import { ProductHeader } from "../../components/product-header";
import { ReportResult } from "./report-result";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="app-shell result-shell">
      <ProductHeader compact />
      <ReportResult reportId={id} />
    </main>
  );
}
