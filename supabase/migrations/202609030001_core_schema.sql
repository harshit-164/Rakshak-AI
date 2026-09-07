-- SIH26165 core data model and owner-isolation boundary.
-- Apply to a test Supabase project before production. All public user data is RLS protected.

create extension if not exists pgcrypto with schema extensions;

create type public.analysis_engine_mode as enum (
  'hosted_baseline',
  'encoder',
  'qwen_adapter',
  'recorded_sample'
);

create type public.analysis_job_status as enum ('queued', 'running', 'completed', 'failed');

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = statement_timestamp();
  return new;
end;
$$;

revoke execute on function public.set_updated_at() from public, anon, authenticated;

create table public.reports (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid(),
  report_group_id uuid not null default gen_random_uuid(),
  version integer not null default 1 check (version > 0),
  narrative text not null check (char_length(narrative) between 20 and 8000),
  normalized_input text not null,
  normalization_version text not null,
  narrative_sha256 text not null check (narrative_sha256 ~ '^[0-9a-f]{64}$'),
  activity text check (activity is null or char_length(activity) between 1 and 120),
  site text check (site is null or char_length(site) between 1 and 120),
  report_date date,
  is_synthetic boolean not null default false,
  demo_dataset_id text,
  predecessor_id uuid,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (id, owner_id),
  unique (owner_id, report_group_id, version),
  foreign key (predecessor_id, owner_id)
    references public.reports (id, owner_id)
    on delete restrict
);

create table public.analysis_jobs (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid(),
  report_id uuid not null,
  engine_mode public.analysis_engine_mode not null,
  status public.analysis_job_status not null default 'queued',
  idempotency_key text not null check (char_length(idempotency_key) between 8 and 200),
  request_sha256 text not null check (request_sha256 ~ '^[0-9a-f]{64}$'),
  attempt_count integer not null default 0 check (attempt_count between 0 and 2),
  lease_token uuid,
  lease_expires_at timestamptz,
  heartbeat_at timestamptz,
  error_code text,
  provider_attempt_metadata jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (id, owner_id),
  unique (owner_id, idempotency_key),
  foreign key (report_id, owner_id)
    references public.reports (id, owner_id)
    on delete cascade,
  check (
    (status = 'running' and lease_token is not null and lease_expires_at is not null)
    or (status <> 'running')
  )
);

create table public.analyses (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  report_id uuid not null,
  job_id uuid not null unique,
  result jsonb not null,
  model_manifest_sha256 text not null check (model_manifest_sha256 ~ '^[0-9a-f]{64}$'),
  input_sha256 text not null check (input_sha256 ~ '^[0-9a-f]{64}$'),
  duration_ms integer not null check (duration_ms >= 0),
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (id, owner_id),
  foreign key (report_id, owner_id)
    references public.reports (id, owner_id)
    on delete cascade,
  foreign key (job_id, owner_id)
    references public.analysis_jobs (id, owner_id)
    on delete cascade
);

create table public.reviews (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid(),
  analysis_id uuid not null,
  reviewer_id uuid not null default auth.uid(),
  sif_label text not null check (sif_label in ('yes', 'no', 'unknown')),
  relevant_rule_ids text[] not null default '{}',
  rules_assessment text not null check (rules_assessment in ('complete', 'partial', 'unknown')),
  unassessed_rule_ids text[] not null default '{}',
  confirmed_breach_ids text[] not null default '{}',
  barrier_tags text[] not null default '{}',
  note text not null check (char_length(note) between 10 and 2000),
  evidence_edits jsonb not null default '[]'::jsonb,
  version integer not null check (version > 0),
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (id, owner_id),
  unique (analysis_id, version),
  foreign key (analysis_id, owner_id)
    references public.analyses (id, owner_id)
    on delete cascade,
  check (reviewer_id = owner_id)
);

create table public.batches (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid(),
  valid_report_ids uuid[] not null default '{}',
  valid_job_ids uuid[] not null default '{}',
  rejected_rows jsonb not null default '[]'::jsonb,
  total_rows integer not null check (total_rows between 0 and 20),
  valid_rows integer not null check (valid_rows >= 0),
  rejected_count integer not null check (rejected_count >= 0),
  status text not null check (status in ('queued', 'running', 'completed', 'partial', 'failed')),
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (id, owner_id),
  check (valid_rows + rejected_count = total_rows)
);

create table public.usage_buckets (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  bucket_kind text not null,
  bucket_start timestamptz not null,
  usage_count integer not null default 0 check (usage_count >= 0),
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (owner_id, bucket_kind, bucket_start)
);

create table public.reference_documents (
  id uuid primary key default gen_random_uuid(),
  source_id text not null unique,
  source_url text,
  title text not null,
  edition text,
  rights_status text not null check (rights_status in ('unresolved', 'restricted', 'cleared')),
  document_sha256 text check (document_sha256 is null or document_sha256 ~ '^[0-9a-f]{64}$'),
  approved_passages jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp()
);

create table public.model_registry (
  id uuid primary key default gen_random_uuid(),
  engine_mode public.analysis_engine_mode not null,
  display_name text not null,
  manifest jsonb not null,
  manifest_sha256 text not null unique check (manifest_sha256 ~ '^[0-9a-f]{64}$'),
  is_active boolean not null default false,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp()
);

create unique index one_active_model on public.model_registry (is_active) where is_active;
create index reports_owner_created_idx on public.reports (owner_id, created_at desc);
create index jobs_queue_idx on public.analysis_jobs (status, created_at) where status = 'queued';
create index jobs_owner_created_idx on public.analysis_jobs (owner_id, created_at desc);
create index analyses_owner_report_idx on public.analyses (owner_id, report_id, created_at desc);
create index reviews_owner_analysis_idx on public.reviews (owner_id, analysis_id, version desc);

create trigger reports_updated_at before update on public.reports
for each row execute function public.set_updated_at();
create trigger jobs_updated_at before update on public.analysis_jobs
for each row execute function public.set_updated_at();
create trigger batches_updated_at before update on public.batches
for each row execute function public.set_updated_at();
create trigger usage_updated_at before update on public.usage_buckets
for each row execute function public.set_updated_at();
create trigger reference_documents_updated_at before update on public.reference_documents
for each row execute function public.set_updated_at();
create trigger model_registry_updated_at before update on public.model_registry
for each row execute function public.set_updated_at();

alter table public.reports enable row level security;
alter table public.analysis_jobs enable row level security;
alter table public.analyses enable row level security;
alter table public.reviews enable row level security;
alter table public.batches enable row level security;
alter table public.usage_buckets enable row level security;
alter table public.reference_documents enable row level security;
alter table public.model_registry enable row level security;

revoke all on table public.reports from anon, authenticated;
revoke all on table public.analysis_jobs from anon, authenticated;
revoke all on table public.analyses from anon, authenticated;
revoke all on table public.reviews from anon, authenticated;
revoke all on table public.batches from anon, authenticated;
revoke all on table public.usage_buckets from anon, authenticated;
revoke all on table public.reference_documents from anon, authenticated;
revoke all on table public.model_registry from anon, authenticated;

grant select, insert on table public.reports to authenticated;
grant select, insert on table public.analysis_jobs to authenticated;
grant select on table public.analyses to authenticated;
grant select, insert on table public.reviews to authenticated;
grant select, insert on table public.batches to authenticated;
grant select on table public.reference_documents to authenticated;
grant select on table public.model_registry to authenticated;

create policy reports_select_own on public.reports
for select to authenticated
using ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy reports_insert_own on public.reports
for insert to authenticated
with check ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy jobs_select_own on public.analysis_jobs
for select to authenticated
using ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy jobs_insert_own on public.analysis_jobs
for insert to authenticated
with check ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy analyses_select_own on public.analyses
for select to authenticated
using ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy reviews_select_own on public.reviews
for select to authenticated
using ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy reviews_insert_own on public.reviews
for insert to authenticated
with check (
  (select auth.uid()) is not null
  and owner_id = (select auth.uid())
  and reviewer_id = (select auth.uid())
);

create policy batches_select_own on public.batches
for select to authenticated
using ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy batches_insert_own on public.batches
for insert to authenticated
with check ((select auth.uid()) is not null and owner_id = (select auth.uid()));

create policy references_read_only on public.reference_documents
for select to authenticated
using (true);

create policy model_registry_read_only on public.model_registry
for select to authenticated
using (true);

comment on table public.reports is 'Immutable safety report input versions owned by one authenticated user.';
comment on table public.analyses is 'Immutable versioned model outputs; service worker writes only.';
comment on table public.reviews is 'Append-only human review decisions; never overwrites an analysis.';
