import type { components } from "./api";

export const SCHEMA_VERSION = "1.0" as const;

export const RULE_IDS = [
  "bypassing_safety_controls",
  "confined_space",
  "driving",
  "energy_isolation",
  "hot_work",
  "line_of_fire",
  "safe_mechanical_lifting",
  "work_authorisation",
  "working_at_height",
] as const;

export type AnalysisResult = components["schemas"]["AnalysisResult"];
export type AnalysisJobCreated = components["schemas"]["AnalysisJobCreated"];
export type AnalysisJobStatus = components["schemas"]["AnalysisJobStatus"];
export type CapabilitiesResponse = components["schemas"]["CapabilitiesResponse"];
export type JobStatusResponse = components["schemas"]["JobStatusResponse"];
export type ModelOutputSubset = components["schemas"]["ModelOutputSubset"];
export type ReportCreate = components["schemas"]["ReportCreate"];
export type ReportCreated = components["schemas"]["ReportCreated"];
export type ReportDetail = components["schemas"]["ReportDetail"];
