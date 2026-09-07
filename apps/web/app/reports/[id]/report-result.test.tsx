import "@testing-library/jest-dom/vitest";
import type { ReportDetail } from "@sih/contracts";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResultContent } from "./report-result";

const detail: ReportDetail = {
  report: {
    id: "report-1",
    report_group_id: "group-1",
    version: 1,
    narrative: "A suspended load passed directly above a worker during the lift.",
    activity: "Mechanical lifting",
    site: null,
    report_date: null,
    is_synthetic: true,
    created_at: "2026-09-03T12:00:00Z",
  },
  analyses: [
    {
      id: "analysis-1",
      job_id: "job-1",
      duration_ms: 420,
      created_at: "2026-09-03T12:00:01Z",
      result: {
        schema_version: "1.0",
        sif_label: "yes",
        abstain_reasons: [],
        model_score: null,
        score_kind: "none",
        relevant_rule_ids: ["line_of_fire", "safe_mechanical_lifting"],
        rules_assessment: "complete",
        unassessed_rule_ids: [],
        rule_scores: null,
        precursors: [{ tag: "overhead_load_exposure", evidence_ids: ["e1"] }],
        barriers: [
          { tag: "separation_from_suspended_load", state: "failed", evidence_ids: ["e1"] },
        ],
        evidence: [
          {
            id: "e1",
            field: "narrative",
            quote: "A suspended load passed directly above a worker",
            method: "llm_extracted",
            occurrence: 0,
          },
        ],
        missing_information: [],
        summary: "A worker was exposed beneath a suspended load.",
        references: [],
        review_status: "pending",
        provenance: {
          engine_mode: "hosted_baseline",
          model_id: "gemini-2.5-flash",
          model_revision: "provider_revision_unavailable",
          prompt_version: "sif-analysis-v1",
          label_guide_version: "sif-pilot-v1",
          auxiliary_models: [],
          inference_is_live: true,
        },
      },
    },
  ],
};

describe("saved report result", () => {
  it("shows the proposal, exact evidence, rules, and live engine identity", () => {
    render(<ResultContent detail={detail} />);

    expect(screen.getByRole("heading", { name: /SIF potential: yes/i })).toBeInTheDocument();
    expect(screen.getAllByText(/A suspended load passed directly above a worker/)).toHaveLength(2);
    expect(screen.getByText("Line of fire")).toBeInTheDocument();
    expect(screen.getByText("Rakshak SIF Engine")).toBeInTheDocument();
    expect(screen.getByText("Live")).toBeInTheDocument();
  });
});
