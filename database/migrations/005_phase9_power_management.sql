-- ============================================================================
-- Migration 005: Autonomous Field Node Power Management & Battery Telemetry (Phase 9)
-- Extends node schema and introduces power history audit logging.
-- Idempotent and safe to run multiple times.
-- ============================================================================

-- 1. Extend nodes table with power management attributes
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS power_mode TEXT DEFAULT 'NORMAL';
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS battery_voltage_v DOUBLE PRECISION;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS battery_state TEXT DEFAULT 'DISCHARGING';
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS solar_available BOOLEAN DEFAULT FALSE;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS telemetry_interval_s INTEGER DEFAULT 300;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS desired_power_profile JSONB DEFAULT '{}'::JSONB;

-- 2. Power Telemetry & Autonomy History Table
CREATE TABLE IF NOT EXISTS public.node_power_history (
    id                          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    node_id                     TEXT NOT NULL,
    power_mode                  TEXT NOT NULL DEFAULT 'NORMAL',
    battery_soc_pct             DOUBLE PRECISION,
    battery_voltage_v           DOUBLE PRECISION,
    battery_state               TEXT DEFAULT 'DISCHARGING',
    charging                    BOOLEAN DEFAULT FALSE,
    solar_available             BOOLEAN DEFAULT FALSE,
    solar_input_power_w         DOUBLE PRECISION,
    estimated_power_w           DOUBLE PRECISION,
    estimated_autonomy_hours    DOUBLE PRECISION,
    telemetry_interval_s        INTEGER DEFAULT 300,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- Indices for rapid querying of node power profiles over time
CREATE INDEX IF NOT EXISTS node_power_history_node_idx
    ON public.node_power_history (node_id, created_at DESC);

CREATE INDEX IF NOT EXISTS node_power_history_mode_idx
    ON public.node_power_history (power_mode);
