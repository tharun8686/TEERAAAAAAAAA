-- ============================================================================
-- Terra Edge — Supabase schema
-- ----------------------------------------------------------------------------
-- Run this once in your Supabase project: Dashboard -> SQL Editor -> New query
-- -> paste -> Run. It is safe to re-run; every statement is idempotent.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- alerts: one row per threshold breach (severity WARNING or CRITICAL)
--
-- Common fields are real columns so they can be indexed and filtered in SQL.
-- The full hazard-specific alert body is kept verbatim in `details`, which is
-- what the /api/alerts endpoints return, so each hazard keeps its own fields
-- (top_features, trigger_values, predicted_pm25_60m, ...) without needing
-- seven separate tables.
-- ---------------------------------------------------------------------------
create table if not exists public.alerts (
    id          bigint generated always as identity primary key,
    alert_id    text        not null,
    hazard      text        not null,
    node_id     text,
    severity    text        not null,
    risk_score  numeric,
    details     jsonb       not null default '{}'::jsonb,
    created_at  timestamptz not null default now()
);

create index if not exists alerts_hazard_created_idx
    on public.alerts (hazard, created_at desc);
create index if not exists alerts_severity_idx
    on public.alerts (severity);

-- ---------------------------------------------------------------------------
-- predictions: every inference, not just the ones that crossed a threshold.
-- This is the history the dashboard can chart over time.
-- Set SUPABASE_LOG_PREDICTIONS=false in .env to skip these writes.
-- ---------------------------------------------------------------------------
create table if not exists public.predictions (
    id          bigint generated always as identity primary key,
    hazard      text        not null,
    node_id     text,
    severity    text,
    risk_score  numeric,
    payload     jsonb       not null default '{}'::jsonb,
    result      jsonb       not null default '{}'::jsonb,
    created_at  timestamptz not null default now()
);

create index if not exists predictions_hazard_created_idx
    on public.predictions (hazard, created_at desc);

-- ---------------------------------------------------------------------------
-- nodes: the field sensor inventory that used to be a hardcoded Python list.
-- Each service upserts its built-in nodes on startup, so this fills itself in.
-- ---------------------------------------------------------------------------
create table if not exists public.nodes (
    node_id     text primary key,
    hazard      text not null,
    type        text,
    zone        text,
    lat         double precision,
    lon         double precision,
    status      text default 'ONLINE',
    last_ping   timestamptz default now()
);

create index if not exists nodes_hazard_idx on public.nodes (hazard);

-- ============================================================================
-- Row Level Security
-- ----------------------------------------------------------------------------
-- The FastAPI services connect with the service_role key, which bypasses RLS
-- entirely, so these policies are not needed for the backends to work. They
-- matter only if you later read these tables straight from the browser with
-- the anon key. The policies below grant public READ and keep writes
-- server-side only.
--
-- Leave this whole block commented out if you would rather keep the tables
-- fully private.
-- ============================================================================

-- alter table public.alerts      enable row level security;
-- alter table public.predictions enable row level security;
-- alter table public.nodes       enable row level security;

-- create policy "public read alerts"      on public.alerts      for select using (true);
-- create policy "public read predictions" on public.predictions for select using (true);
-- create policy "public read nodes"       on public.nodes       for select using (true);

-- ============================================================================
-- Handy queries once data starts flowing
-- ============================================================================
-- Most recent alerts across every hazard:
--   select hazard, alert_id, node_id, severity, risk_score, created_at
--   from public.alerts order by created_at desc limit 50;
--
-- Alert counts by hazard and severity:
--   select hazard, severity, count(*) from public.alerts
--   group by hazard, severity order by hazard;
--
-- Risk trend for one hazard over the last day:
--   select date_trunc('hour', created_at) as hour, avg(risk_score) as avg_risk
--   from public.predictions
--   where hazard = 'flood' and created_at > now() - interval '1 day'
--   group by hour order by hour;
