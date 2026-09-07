-- Atomic per-owner demo limits. Idempotent replays return before counters are consumed.

create or replace function public.consume_usage_v1(
  p_owner_id uuid,
  p_bucket_kind text,
  p_bucket_start timestamptz,
  p_limit integer,
  p_amount integer default 1
)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_count integer;
begin
  if p_owner_id is null or p_limit < 1 or p_amount < 1 or p_amount > p_limit then
    return false;
  end if;

  insert into public.usage_buckets (
    owner_id, bucket_kind, bucket_start, usage_count
  ) values (
    p_owner_id, p_bucket_kind, p_bucket_start, p_amount
  )
  on conflict (owner_id, bucket_kind, bucket_start) do update
  set usage_count = public.usage_buckets.usage_count + excluded.usage_count,
      updated_at = statement_timestamp()
  where public.usage_buckets.usage_count + excluded.usage_count <= p_limit
  returning usage_count into v_count;

  return v_count is not null;
end;
$$;

revoke execute on function public.consume_usage_v1(uuid, text, timestamptz, integer, integer)
  from public, anon, authenticated;

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

  if not public.consume_usage_v1(
    v_owner,
    'report_submission_minute',
    date_trunc('minute', statement_timestamp()),
    10,
    1
  ) then
    raise exception using errcode = 'P0001', message = 'quota_report_per_minute';
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

  select * into v_job
  from public.analysis_jobs
  where owner_id = v_owner and idempotency_key = p_idempotency_key;

  if v_job.id is not null then
    if v_job.request_sha256 <> p_request_sha256 then
      raise exception using errcode = '23505', message = 'idempotency_payload_conflict';
    end if;
    return query select v_job.id, v_job.status, true;
    return;
  end if;

  if not exists (
    select 1 from public.reports where id = p_report_id and owner_id = v_owner
  ) then
    raise exception using errcode = 'P0002', message = 'report_not_found';
  end if;

  if not public.consume_usage_v1(
    v_owner,
    'analysis_job_day',
    date_trunc('day', statement_timestamp()),
    100,
    1
  ) then
    raise exception using errcode = 'P0001', message = 'quota_analysis_per_day';
  end if;

  if (
    select count(*) from public.analysis_jobs
    where owner_id = v_owner and status in ('queued', 'running')
  ) >= 2 then
    raise exception using errcode = 'P0001', message = 'active_job_limit';
  end if;

  insert into public.analysis_jobs (
    owner_id, report_id, engine_mode, idempotency_key, request_sha256
  ) values (
    v_owner, p_report_id, p_engine_mode, p_idempotency_key, p_request_sha256
  )
  returning * into v_job;

  return query select v_job.id, v_job.status, false;
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
      provider_attempt_metadata = provider_attempt_metadata || jsonb_build_array(
        jsonb_build_object(
          'attempt', attempt_count + 1,
          'claimed_at', statement_timestamp(),
          'remote_call_may_repeat_after_crash', true
        )
      ),
      updated_at = statement_timestamp()
  where id = v_job_id
  returning *;
end;
$$;
