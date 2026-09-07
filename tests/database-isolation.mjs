import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { PGlite } from "@electric-sql/pglite";

const migrationsUrl = new URL("../supabase/migrations/", import.meta.url);
const migrationFiles = (await readdir(migrationsUrl)).filter((name) => name.endsWith(".sql")).sort();
const db = new PGlite();

await db.exec(`
  create schema if not exists extensions;
  create schema if not exists auth;
  create role anon nologin;
  create role authenticated nologin;
  create role service_role nologin bypassrls;
  create function auth.uid() returns uuid language sql stable as $$
    select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
  $$;
`);

for (const migrationFile of migrationFiles) {
  const migration = await readFile(new URL(migrationFile, migrationsUrl), "utf8");
  const portableMigration = migration.replace(
    "create extension if not exists pgcrypto with schema extensions;",
    "-- pgcrypto is preinstalled by Supabase and omitted only in the PGlite contract test",
  );
  await db.exec(portableMigration);
}

const ownerA = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const ownerB = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

async function asUser(ownerId, sql, params = []) {
  await db.exec("reset role");
  await db.query("select set_config('request.jwt.claim.sub', $1, false)", [ownerId]);
  await db.exec("set role authenticated");
  try {
    return await db.query(sql, params);
  } finally {
    await db.exec("reset role");
  }
}

const narrative = "A worker walked below a suspended load during a planned lifting task.";
const normalized = narrative;
const hash = "a".repeat(64);

const inserted = await asUser(
  ownerA,
  `select * from public.create_report_v1(
    $1, $2, $3, $4, $5, $6, null, null, null, true
  )`,
  ["report-key-a", hash, narrative, normalized, "input-normalization-v1", hash],
);
assert.equal(inserted.rows.length, 1);
assert.equal(inserted.rows[0].replayed, false);

const replayed = await asUser(
  ownerA,
  `select * from public.create_report_v1(
    $1, $2, $3, $4, $5, $6, null, null, null, true
  )`,
  ["report-key-a", hash, narrative, normalized, "input-normalization-v1", hash],
);
assert.equal(replayed.rows[0].report_id, inserted.rows[0].report_id);
assert.equal(replayed.rows[0].replayed, true);

await assert.rejects(
  asUser(
    ownerA,
    `select * from public.create_report_v1(
      $1, $2, $3, $4, $5, $6, null, null, null, true
    )`,
    ["report-key-a", "b".repeat(64), narrative, normalized, "input-normalization-v1", hash],
  ),
  /idempotency_payload_conflict/i,
);

const ownRows = await asUser(ownerA, "select id from public.reports");
const otherRows = await asUser(ownerB, "select id from public.reports");
assert.equal(ownRows.rows.length, 1);
assert.equal(otherRows.rows.length, 0);

await assert.rejects(
  asUser(
    ownerB,
    `insert into public.reports
      (owner_id, narrative, normalized_input, normalization_version, narrative_sha256)
     values
      ('${ownerA}', '${narrative}', '${normalized}', 'input-normalization-v1', '${hash}')`,
  ),
  /row-level security policy|permission denied/i,
);

for (let index = 2; index <= 10; index += 1) {
  const requestHash = index.toString(16).padStart(64, "0");
  const result = await asUser(
    ownerA,
    `select * from public.create_report_v1(
      $1, $2, $3, $4, $5, $6, null, null, null, true
    )`,
    [`report-key-${index}`, requestHash, narrative, normalized, "input-normalization-v1", hash],
  );
  assert.equal(result.rows[0].replayed, false);
}

await assert.rejects(
  asUser(
    ownerA,
    `select * from public.create_report_v1(
      $1, $2, $3, $4, $5, $6, null, null, null, true
    )`,
    ["report-key-11", "b".repeat(64), narrative, normalized, "input-normalization-v1", hash],
  ),
  /quota_report_per_minute/i,
);

const reportId = inserted.rows[0].report_id;
const firstJob = await asUser(
  ownerA,
  "select * from public.create_analysis_job_v1($1, 'hosted_baseline', $2, $3)",
  [reportId, "analysis-key-1", "c".repeat(64)],
);
const replayedJob = await asUser(
  ownerA,
  "select * from public.create_analysis_job_v1($1, 'hosted_baseline', $2, $3)",
  [reportId, "analysis-key-1", "c".repeat(64)],
);
assert.equal(replayedJob.rows[0].job_id, firstJob.rows[0].job_id);
assert.equal(replayedJob.rows[0].replayed, true);

await asUser(
  ownerA,
  "select * from public.create_analysis_job_v1($1, 'hosted_baseline', $2, $3)",
  [reportId, "analysis-key-2", "d".repeat(64)],
);
await assert.rejects(
  asUser(
    ownerA,
    "select * from public.create_analysis_job_v1($1, 'hosted_baseline', $2, $3)",
    [reportId, "analysis-key-3", "e".repeat(64)],
  ),
  /active_job_limit/i,
);
await assert.rejects(
  asUser(
    ownerB,
    "select * from public.create_analysis_job_v1($1, 'hosted_baseline', $2, $3)",
    [reportId, "analysis-key-b", "f".repeat(64)],
  ),
  /report_not_found/i,
);

const minuteUsage = await db.query(
  "select usage_count from public.usage_buckets where owner_id = $1 and bucket_kind = 'report_submission_minute'",
  [ownerA],
);
const dailyUsage = await db.query(
  "select usage_count from public.usage_buckets where owner_id = $1 and bucket_kind = 'analysis_job_day'",
  [ownerA],
);
assert.equal(minuteUsage.rows[0].usage_count, 10);
assert.equal(dailyUsage.rows[0].usage_count, 2);

console.log("database isolation, idempotency, and atomic quota checks: PASS");
await db.close();
