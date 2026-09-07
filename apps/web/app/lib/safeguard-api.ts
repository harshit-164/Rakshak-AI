"use client";

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type {
  AnalysisJobCreated,
  JobStatusResponse,
  ReportCreate,
  ReportCreated,
  ReportDetail,
} from "@sih/contracts";

type ErrorEnvelope = {
  error?: { code?: string; message?: string; retryable?: boolean; request_id?: string };
};

let supabase: SupabaseClient | null = null;

export function isBrowserSafeSupabaseKey(key: string | undefined): key is string {
  return Boolean(key && !key.startsWith("sb_secret_"));
}

export class SafeguardApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly retryable: boolean,
  ) {
    super(message);
  }
}

function browserClient(): SupabaseClient {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !isBrowserSafeSupabaseKey(anonKey)) {
    throw new SafeguardApiError(
      anonKey?.startsWith("sb_secret_")
        ? "Supabase is misconfigured: use a publishable or anon key for browser access, never an sb_secret key."
        : "Anonymous demo access is not configured yet.",
      "auth_unconfigured",
      false,
    );
  }
  supabase ??= createClient(url, anonKey, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
  });
  return supabase;
}

export async function demoAccessToken(): Promise<string> {
  const client = browserClient();
  const existing = await client.auth.getSession();
  if (existing.error) {
    throw new SafeguardApiError(existing.error.message, "session_error", true);
  }
  if (existing.data.session) return existing.data.session.access_token;

  const created = await client.auth.signInAnonymously();
  if (created.error || !created.data.session) {
    throw new SafeguardApiError(
      created.error?.message ?? "Could not start the anonymous demo session.",
      "session_error",
      true,
    );
  }
  return created.data.session.access_token;
}

async function apiRequest<T>(
  path: string,
  accessToken: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`/api/backend/v1${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });
  if (!response.ok) {
    let problem: ErrorEnvelope = {};
    try {
      problem = (await response.json()) as ErrorEnvelope;
    } catch {
      // The stable fallback below deliberately avoids exposing a proxy response body.
    }
    throw new SafeguardApiError(
      problem.error?.message ?? "The analysis request failed.",
      problem.error?.code ?? "request_failed",
      problem.error?.retryable ?? response.status >= 500,
    );
  }
  return (await response.json()) as T;
}

export function createReport(
  value: ReportCreate,
  accessToken: string,
  idempotencyKey: string,
): Promise<ReportCreated> {
  return apiRequest<ReportCreated>("/reports", accessToken, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify(value),
  });
}

export function queueAnalysis(
  reportId: string,
  accessToken: string,
  idempotencyKey: string,
): Promise<AnalysisJobCreated> {
  return apiRequest<AnalysisJobCreated>(`/reports/${reportId}/analyses`, accessToken, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({ engine_mode: "hosted_baseline" }),
  });
}

export function getJob(jobId: string, accessToken: string): Promise<JobStatusResponse> {
  return apiRequest<JobStatusResponse>(`/jobs/${jobId}`, accessToken);
}

export function getReport(reportId: string, accessToken: string): Promise<ReportDetail> {
  return apiRequest<ReportDetail>(`/reports/${reportId}`, accessToken);
}
