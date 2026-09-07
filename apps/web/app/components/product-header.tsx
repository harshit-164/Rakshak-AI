import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export function ProductHeader({ compact = false }: { compact?: boolean }) {
  return (
    <header className={compact ? "site-header app-site-header" : "site-header"}>
      <Link className="brand" href="/" aria-label="Rakshak AI home">
        <span className="brand-mark">
          <ShieldCheck size={18} strokeWidth={2.2} />
        </span>
        <span>RAKSHAK<span className="brand-ai">.AI</span></span>
      </Link>
      <nav className="primary-nav" aria-label="Primary navigation">
        <Link href="/analyze">New analysis</Link>
        <span className="model-pill">Rakshak SIF Engine / v1</span>
      </nav>
    </header>
  );
}
