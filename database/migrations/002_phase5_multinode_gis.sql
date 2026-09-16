-- ============================================================================
-- Migration 002: Multi-Node GIS and Spatial Aggregation Extensions (Phase 5)
-- ============================================================================

ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS state TEXT DEFAULT 'Tamil Nadu';
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS zone TEXT;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS battery DOUBLE PRECISION;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS capabilities TEXT[] DEFAULT '{}';
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS firmware_version TEXT DEFAULT '1.0.0';
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS is_simulated BOOLEAN DEFAULT FALSE;
ALTER TABLE public.nodes ADD COLUMN IF NOT EXISTS gateway_id TEXT DEFAULT 'GW-01';

CREATE INDEX IF NOT EXISTS nodes_district_idx ON public.nodes (district);
CREATE INDEX IF NOT EXISTS nodes_state_idx ON public.nodes (state);
CREATE INDEX IF NOT EXISTS nodes_gateway_idx ON public.nodes (gateway_id);

ALTER TABLE public.predictions ADD COLUMN IF NOT EXISTS state TEXT DEFAULT 'Tamil Nadu';
ALTER TABLE public.predictions ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE public.predictions ADD COLUMN IF NOT EXISTS gateway_id TEXT DEFAULT 'GW-01';

CREATE INDEX IF NOT EXISTS predictions_district_created_idx
    ON public.predictions (district, created_at DESC);
CREATE INDEX IF NOT EXISTS predictions_gateway_idx
    ON public.predictions (gateway_id);

ALTER TABLE public.alerts ADD COLUMN IF NOT EXISTS state TEXT DEFAULT 'Tamil Nadu';
ALTER TABLE public.alerts ADD COLUMN IF NOT EXISTS district TEXT;
ALTER TABLE public.alerts ADD COLUMN IF NOT EXISTS gateway_id TEXT DEFAULT 'GW-01';

CREATE INDEX IF NOT EXISTS alerts_district_idx ON public.alerts (district);
CREATE INDEX IF NOT EXISTS alerts_gateway_idx ON public.alerts (gateway_id);
