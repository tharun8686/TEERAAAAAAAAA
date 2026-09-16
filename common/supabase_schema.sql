-- ============================================================================
-- Terra Edge — Supabase schema (Phase 5 Multi-Node & District GIS)
-- ----------------------------------------------------------------------------
-- Run this once in your Supabase project: Dashboard -> SQL Editor -> New query
-- -> paste -> Run. It is safe to re-run; every statement is idempotent.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- alerts: one row per threshold breach (severity WARNING or CRITICAL)
-- ---------------------------------------------------------------------------
create table if not exists public.alerts (
    id          bigint generated always as identity primary key,
    alert_id    text        not null,
    hazard      text        not null,
    node_id     text,
    state       text        default 'Tamil Nadu',
    district    text,
    gateway_id  text        default 'GW-01',
    severity    text        not null,
    risk_score  numeric,
    details     jsonb       not null default '{}'::jsonb,
    created_at  timestamptz not null default now()
);

create index if not exists alerts_hazard_created_idx
    on public.alerts (hazard, created_at desc);
create index if not exists alerts_severity_idx
    on public.alerts (severity);
create index if not exists alerts_district_idx
    on public.alerts (district);

-- ---------------------------------------------------------------------------
-- predictions: every inference, not just the ones that crossed a threshold.
-- This is the history the dashboard can chart over time.
-- Set SUPABASE_LOG_PREDICTIONS=false in .env to skip these writes.
-- ---------------------------------------------------------------------------
create table if not exists public.predictions (
    id          bigint generated always as identity primary key,
    hazard      text        not null,
    node_id     text,
    state       text        default 'Tamil Nadu',
    district    text,
    gateway_id  text        default 'GW-01',
    severity    text,
    risk_score  numeric,
    payload     jsonb       not null default '{}'::jsonb,
    result      jsonb       not null default '{}'::jsonb,
    created_at  timestamptz not null default now()
);

create index if not exists predictions_hazard_created_idx
    on public.predictions (hazard, created_at desc);
create index if not exists predictions_district_created_idx
    on public.predictions (district, created_at desc);

-- ---------------------------------------------------------------------------
-- nodes: the field sensor inventory table supporting dynamic registration.
-- ---------------------------------------------------------------------------
create table if not exists public.nodes (
    node_id          text primary key,
    hazard           text not null default 'all',
    type             text default 'Type-A',
    state            text default 'Tamil Nadu',
    district         text,
    zone             text,
    lat              double precision,
    lon              double precision,
    battery          double precision,
    capabilities     text[] default '{}',
    firmware_version text default '1.0.0',
    is_simulated     boolean default false,
    gateway_id       text default 'GW-01',
    status           text default 'ONLINE',
    last_ping        timestamptz default now()
);

create index if not exists nodes_hazard_idx on public.nodes (hazard);
create index if not exists nodes_district_idx on public.nodes (district);
create index if not exists nodes_state_idx on public.nodes (state);

-- ============================================================================
-- Alter existing tables if they already exist (safe migration path)
-- ============================================================================
alter table public.nodes add column if not exists state text default 'Tamil Nadu';
alter table public.nodes add column if not exists district text;
alter table public.nodes add column if not exists battery double precision;
alter table public.nodes add column if not exists capabilities text[] default '{}';
alter table public.nodes add column if not exists firmware_version text default '1.0.0';
alter table public.nodes add column if not exists is_simulated boolean default false;
alter table public.nodes add column if not exists gateway_id text default 'GW-01';

alter table public.predictions add column if not exists state text default 'Tamil Nadu';
alter table public.predictions add column if not exists district text;
alter table public.predictions add column if not exists gateway_id text default 'GW-01';

alter table public.alerts add column if not exists state text default 'Tamil Nadu';
alter table public.alerts add column if not exists district text;
alter table public.alerts add column if not exists gateway_id text default 'GW-01';

-- ---------------------------------------------------------------------------
-- notification_targets: registered emergency response authority contacts
-- ---------------------------------------------------------------------------
create table if not exists public.notification_targets (
    target_id    text primary key,
    target_type  text not null,
    name         text not null,
    destination  text not null,
    state        text default 'Tamil Nadu',
    district     text,
    hazards      text[] default '{"all"}',
    min_severity text default 'WARNING',
    enabled      boolean default true,
    created_at   timestamptz default now()
);

create index if not exists targets_type_idx on public.notification_targets (target_type);
create index if not exists targets_district_idx on public.notification_targets (district);

-- ---------------------------------------------------------------------------
-- notification_dispatches: complete audit log of every channel dispatch attempt
-- ---------------------------------------------------------------------------
create table if not exists public.notification_dispatches (
    dispatch_id         text primary key,
    alert_id            text not null,
    channel             text not null,
    target              text not null,
    attempted_at        timestamptz default now(),
    status              text not null,
    provider_message_id text,
    error               text,
    latency_ms          numeric default 0.0,
    dry_run             boolean default true,
    response_metadata   jsonb default '{}'::jsonb
);

create index if not exists dispatches_alert_idx on public.notification_dispatches (alert_id);
create index if not exists dispatches_channel_idx on public.notification_dispatches (channel);
create index if not exists dispatches_attempted_at_idx on public.notification_dispatches (attempted_at desc);

