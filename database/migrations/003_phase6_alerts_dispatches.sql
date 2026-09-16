-- ============================================================================
-- Migration 003: Multi-Channel Alerting & Dispatch Audit Tables (Phase 6)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.notification_targets (
    target_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    target_type     TEXT NOT NULL,
    destination     TEXT NOT NULL,
    district        TEXT,
    hazard_filter   TEXT[] DEFAULT '{}',
    min_severity    TEXT DEFAULT 'WARNING',
    enabled         BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS notification_targets_type_idx ON public.notification_targets (target_type);
CREATE INDEX IF NOT EXISTS notification_targets_district_idx ON public.notification_targets (district);

CREATE TABLE IF NOT EXISTS public.notification_dispatches (
    dispatch_id         TEXT PRIMARY KEY,
    alert_id            TEXT NOT NULL,
    channel             TEXT NOT NULL,
    target              TEXT NOT NULL,
    attempted_at        TIMESTAMPTZ DEFAULT NOW(),
    status              TEXT NOT NULL,
    provider_message_id TEXT,
    error               TEXT,
    latency_ms          DOUBLE PRECISION DEFAULT 0.0,
    dry_run             BOOLEAN DEFAULT TRUE,
    response_metadata   JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS dispatches_alert_idx ON public.notification_dispatches (alert_id);
CREATE INDEX IF NOT EXISTS dispatches_attempted_idx ON public.notification_dispatches (attempted_at DESC);
CREATE INDEX IF NOT EXISTS dispatches_status_idx ON public.notification_dispatches (status);
