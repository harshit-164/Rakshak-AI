-- Idempotent report/job creation and durable worker lease functions.

create table public.request_idempotency (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  operation text not null,
  idempotency_key text not null check (char_length(idempotency_key) between 8 and 200),
  request_sha256 text not null check (request_sha256 ~ '^[0-9a-f]{64}$'),
  resource_id uuid,
  created_at timestamptz not null default statement_timestamp(),
  updated_at timestamptz not null default statement_timestamp(),
  unique (owner_id, operation, idempotency_key)
);

alter table public.request_idempotency enable row level security;
revoke all on table public.request_idempotency from anon, authenticated;

create or replace function public.create_report_v1(
  p_idempotency_key text,
  p_request_sha256 text,
  p_narrative text,
  p_normalized_input text,
  p_normalization_version text,
  p_narrative_sha256 text,
  p_activity text default null,
  p_site text default null,
  p_report_date date default null,
  p_is_synthetic boolean default false
)
returns table (report_id uuid, report_version integer, replayed boolean)
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_owner uuid := auth.uid();
  v_stored_sha text;
  v_resource_id uuid;
  v_version integer;
begin
  if v_owner is null then
    raise exception using errcode = '28000', message = 'authentication_required';
  end if;

  insert into public.request_idempotency (
    owner_id, operation, idempotency_key, request_sha256
  ) values (
    v_owner, 'create_report', p_idempotency_key, p_request_sha256
  ) on conflict (owner_id, operation, idempotency_key) do nothing;

  select request_sha256, resource_id
  into v_stored_sha, v_resource_id
  from public.request_idempotency
  where owner_id = v_owner
    and operation = 'create_report'
    and idempotency_key = p_idempotency_key
  for update;

  if v_stored_sha <> p_request_sha256 then
    raise exception using errcode = '23505', message = 'idempotency_payload_conflict';
  end if;

  if v_resource_id is not null then
    select version into v_version
    from public.reports
    where id = v_resource_id and owner_id = v_owner;
    return query select v_resource_id, v_version, true;
    return;
  end if;

  insert into public.reports (
    owner_id,
    narrative,
    normalized_input,
    normalization_version,
    narrative_sha256,
    activity,
    site,
    report_date,
    is_synthetic
  ) values (
    v_owner,
    p_narrative,
    p_normalized_input,
    p_normalization_version,
    p_narrative_sha256,
    p_activity,
    p_site,
    p_report_date,
    p_is_synthetic
  ) returning id, version into v_resource_id, v_version;

  update public.request_idempotency
  set resource_id = v_resource_id, updated_at = statement_timestamp()
  where owner_id = v_owner
    and operation = 'create_report'
    and idempotency_key = p_idempotency_key;

  return query select v_resource_id, v_version, false;
end;
$$;

create or replace function public.create_analysis_job_v1(
  p_report_id uuid,
  p_engine_mode public.analysis_engine_mode,
  p_idempotency_key text,
  p_request_sha256 text
)
returns table (job_id uuid, job_status public.analysis_job_status, replayed boolean)
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_owner uuid := auth.uid();
  v_job public.analysis_jobs;
begin
  if v_owner is null then
    raise exception using errcode = '28000', message = 'authentication_required';
  end if;
  if p_engine_mode = 'recorded_sample' then
    raise exception using errcode = '22023', message = 'recorded_sample_rejects_new_reports';
  end if;
  if not exists (
    select 1 from public.reports where id = p_report_id and owner_id = v_owner
  ) then
    raise exception using errcode = 'P0002', message = 'report_not_found';
  end if;

  insert into public.analysis_jobs (
    owner_id, report_id, engine_mode, idempotency_key, request_sha256
  ) values (
    v_owner, p_report_id, p_engine_mode, p_idempotency_key, p_request_sha256
  )
  on conflict (owner_id, idempotency_key) do nothing
  returning * into v_job;

  if v_job.id is not null then
    return query select v_job.id, v_job.status, false;
    return;
  end if;

  select * into v_job
  from public.analysis_jobs
  where owner_id = v_owner and idempotency_key = p_idempotency_key;

  if v_job.request_sha256 <> p_request_sha256 then
    raise exception using errcode = '23505', message = 'idempotency_payload_conflict';
  end if;
  return query select v_job.id, v_job.status, true;
end;
$$;

create or replace function public.claim_analysis_job_v1()
returns setof public.analysis_jobs
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_job_id uuid;
begin
  update public.analysis_jobs
  set status = 'failed',
      error_code = 'attempt_limit_exhausted',
      lease_token = null,
      lease_expires_at = null,
      updated_at = statement_timestamp()
  where status = 'running'
    and lease_expires_at < statement_timestamp()
    and attempt_count >= 2;

  select id into v_job_id
  from public.analysis_jobs
  where (
    status = 'queued'
    or (status = 'running' and lease_expires_at < statement_timestamp())
  )
    and attempt_count < 2
  order by created_at
  for update skip locked
  limit 1;

  if v_job_id is null then
    return;
  end if;

  return query
  update public.analysis_jobs
  set status = 'running',
      attempt_count = attempt_count + 1,
      lease_token = gen_random_uuid(),
      lease_expires_at = statement_timestamp() + interval '180 seconds',
      heartbeat_at = statement_timestamp(),
      error_code = null,
      updated_at = statement_timestamp()
  where id = v_job_id
  returning *;
end;
$$;

create or replace function public.heartbeat_analysis_job_v1(
  p_job_id uuid,
  p_lease_token uuid
)
returns boolean
language sql
security definer
set search_path = ''
as $$
  with heartbeat as (
    update public.analysis_jobs
    set heartbeat_at = statement_timestamp(),
        lease_expires_at = statement_timestamp() + interval '180 seconds',
        updated_at = statement_timestamp()
    where id = p_job_id
      and status = 'running'
      and lease_token = p_lease_token
      and lease_expires_at >= statement_timestamp()
    returning 1
  )
  select exists (select 1 from heartbeat);
$$;

create or replace function public.finalize_analysis_job_v1(
  p_job_id uuid,
  p_lease_token uuid,
  p_result jsonb,
  p_model_manifest_sha256 text,
  p_input_sha256 text,
  p_duration_ms integer
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_job public.analysis_jobs;
  v_analysis_id uuid;
begin
  select * into v_job
  from public.analysis_jobs
  where id = p_job_id
  for update;

  if v_job.id is null then
    raise exception using errcode = 'P0002', message = 'job_not_found';
  end if;

  if v_job.status = 'completed' then
    select id into v_analysis_id from public.analyses where job_id = p_job_id;
    return v_analysis_id;
  end if;

  if v_job.status <> 'running'
     or v_job.lease_token <> p_lease_token
     or v_job.lease_expires_at < statement_timestamp() then
    raise exception using errcode = '55000', message = 'invalid_or_expired_lease';
  end if;

  insert into public.analyses (
    owner_id,
    report_id,
    job_id,
    result,
    model_manifest_sha256,
    input_sha256,
    duration_ms
  ) values (
    v_job.owner_id,
    v_job.report_id,
    v_job.id,
    p_result,
    p_model_manifest_sha256,
    p_input_sha256,
    p_duration_ms
  )
  on conflict (job_id) do nothing
  returning id into v_analysis_id;

  if v_analysis_id is null then
    select id into v_analysis_id from public.analyses where job_id = p_job_id;
  end if;

  update public.analysis_jobs
  set status = 'completed',
      lease_token = null,
      lease_expires_at = null,
      heartbeat_at = statement_timestamp(),
      error_code = null,
      updated_at = statement_timestamp()
  where id = p_job_id and lease_token = p_lease_token;

  return v_analysis_id;
end;
$$;

create or replace function public.fail_analysis_job_v1(
  p_job_id uuid,
  p_lease_token uuid,
  p_error_code text
)
returns boolean
language sql
security definer
set search_path = ''
as $$
  with failed as (
    update public.analysis_jobs
    set status = 'failed',
        error_code = left(p_error_code, 80),
        lease_token = null,
        lease_expires_at = null,
        updated_at = statement_timestamp()
    where id = p_job_id
      and status = 'running'
      and lease_token = p_lease_token
    returning 1
  )
  select exists (select 1 from failed);
$$;

revoke execute on function public.create_report_v1(
  text, text, text, text, text, text, text, text, date, boolean
) from public, anon;
grant execute on function public.create_report_v1(
  text, text, text, text, text, text, text, text, date, boolean
) to authenticated;

revoke execute on function public.create_analysis_job_v1(
  uuid, public.analysis_engine_mode, text, text
) from public, anon;
grant execute on function public.create_analysis_job_v1(
  uuid, public.analysis_engine_mode, text, text
) to authenticated;

revoke execute on function public.claim_analysis_job_v1() from public, anon, authenticated;
revoke execute on function public.heartbeat_analysis_job_v1(uuid, uuid)
  from public, anon, authenticated;
revoke execute on function public.finalize_analysis_job_v1(
  uuid, uuid, jsonb, text, text, integer
) from public, anon, authenticated;
revoke execute on function public.fail_analysis_job_v1(uuid, uuid, text)
  from public, anon, authenticated;

grant execute on function public.claim_analysis_job_v1() to service_role;
grant execute on function public.heartbeat_analysis_job_v1(uuid, uuid) to service_role;
grant execute on function public.finalize_analysis_job_v1(
  uuid, uuid, jsonb, text, text, integer
) to service_role;
grant execute on function public.fail_analysis_job_v1(uuid, uuid, text) to service_role;
