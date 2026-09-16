-- ============================================================================
-- Migration 004: Production Hardening, Audit Trail & Model Registry (Phase 8)
-- ============================================================================

-- Model Metadata Table (Registry tracking for 7 ML hazard models)
CREATE TABLE IF NOT EXISTS public.model_registry (
    hazard                  TEXT PRIMARY KEY,
    model_version           TEXT NOT NULL,
    artifact_version        TEXT NOT NULL,
    algorithm               TEXT NOT NULL,
    feature_schema_version  TEXT NOT NULL DEFAULT '1.0',
    trained_at              TIMESTAMPTZ,
    primary_features        TEXT[] DEFAULT '{}',
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Gateway Auditing & System Events Table
CREATE TABLE IF NOT EXISTS public.gateway_system_events (
    event_id        TEXT PRIMARY KEY,
    gateway_id      TEXT NOT NULL DEFAULT 'GW-01',
    event_type      TEXT NOT NULL,
    severity        TEXT NOT NULL DEFAULT 'INFO',
    details         JSONB DEFAULT '{}'::JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS system_events_type_created_idx
    ON public.gateway_system_events (event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS system_events_gateway_idx
    ON public.gateway_system_events (gateway_id);
