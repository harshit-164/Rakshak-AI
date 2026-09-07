begin;
select plan(12);

select has_table('public', 'reports', 'reports table exists');
select has_table('public', 'analysis_jobs', 'analysis jobs table exists');
select has_table('public', 'analyses', 'analyses table exists');
select has_table('public', 'reviews', 'reviews table exists');
select has_column('public', 'reports', 'owner_id', 'reports carry owner identity');
select has_column('public', 'analysis_jobs', 'owner_id', 'jobs carry owner identity');
select has_column('public', 'analyses', 'owner_id', 'analyses carry owner identity');
select has_column('public', 'reviews', 'owner_id', 'reviews carry owner identity');
select policies_are(
  'public',
  'reports',
  array['reports_insert_own', 'reports_select_own'],
  'reports expose only owner-scoped policies'
);
select policies_are(
  'public',
  'analysis_jobs',
  array['jobs_insert_own', 'jobs_select_own'],
  'jobs expose only owner-scoped policies'
);
select policies_are(
  'public',
  'analyses',
  array['analyses_select_own'],
  'analyses are read-only and owner scoped'
);
select policies_are(
  'public',
  'reviews',
  array['reviews_insert_own', 'reviews_select_own'],
  'reviews are append-only and owner scoped'
);

select * from finish();
rollback;
