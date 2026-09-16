-- ============================================================================
-- Migration 001: Initial Schema (Phase 1 Base Tables)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.alerts (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_id    TEXT NOT NULL,
    hazard      TEXT NOT NULL,
    node_id     TEXT,
    severity    TEXT NOT NULL,
    risk_score  NUMERIC,
    details     JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS alerts_hazard_created_idx
    ON public.alerts (hazard, created_at DESC);
CREATE INDEX IF NOT EXISTS alerts_severity_idx
    ON public.alerts (severity);

CREATE TABLE IF NOT EXISTS public.predictions (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hazard      TEXT NOT NULL,
    node_id     TEXT,
    severity    TEXT,
    risk_score  NUMERIC,
    payload     JSONB NOT NULL DEFAULT '{}'::JSONB,
    result      JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS predictions_hazard_created_idx
    ON public.predictions (hazard, created_at DESC);

CREATE TABLE IF NOT EXISTS public.nodes (
    node_id     TEXT PRIMARY KEY,
    hazard      TEXT NOT NULL DEFAULT 'all',
    type        TEXT DEFAULT 'Type-A',
    lat         DOUBLE PRECISION,
    lon         DOUBLE PRECISION,
    status      TEXT DEFAULT 'ONLINE',
    last_ping   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS nodes_hazard_idx ON public.nodes (hazard);
