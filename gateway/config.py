"""
TerraEdge — Gateway Configuration Module (Phase 8 Production Hardening).
Loads environment variables, centralizes configuration hierarchy,
and provides startup validation for Development, Test, Demo, and Production modes.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple

def _find_and_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        env_path = os.path.join(here, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=False)
            return
        parent = os.path.dirname(here)
        if parent == here:
            return
        here = parent

_find_and_load_dotenv()

# ============================================================================
# Core Environment & Identity Settings
# ============================================================================
TERRAEDGE_ENV: str = os.getenv("TERRAEDGE_ENV", os.getenv("GATEWAY_ENV", "development")).lower()
GATEWAY_ENV: str = TERRAEDGE_ENV  # Backward compatibility alias

GATEWAY_ID: str = os.getenv("GATEWAY_ID", "GW-01").strip()
SITE_NAME: str = os.getenv("SITE_NAME", "Western Ghats Monitoring Station").strip()
DEPLOYMENT_REGION: str = os.getenv("DEPLOYMENT_REGION", "Tamil Nadu").strip()

GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))

# Project Root Directory
GATEWAY_DIR: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT: str = os.path.dirname(GATEWAY_DIR)

# Temporal History Settings
MAX_HISTORY_PER_NODE: int = int(os.getenv("MAX_HISTORY_PER_NODE", "30"))

# ============================================================================
# Security, Tokens & CORS Configuration (Phase 8)
# ============================================================================
ADMIN_TOKEN: str = os.getenv("TERRAEDGE_ADMIN_TOKEN", os.getenv("NOTIFICATION_ADMIN_TOKEN", "terraedge-admin-secret-2026")).strip()
OPERATOR_TOKEN: str = os.getenv("TERRAEDGE_OPERATOR_TOKEN", "terraedge-operator-secret-2026").strip()
SENSOR_TOKEN: str = os.getenv("TERRAEDGE_SENSOR_TOKEN", "terraedge-sensor-secret-2026").strip()
NOTIFICATION_ADMIN_TOKEN: str = ADMIN_TOKEN  # Backward compatibility alias

_raw_origins = os.getenv(
    "TERRAEDGE_ALLOWED_ORIGINS",
    "http://localhost,http://127.0.0.1,http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"
)
ALLOWED_ORIGINS: List[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Rate Limiting & Input Size Limits
RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
RATE_LIMIT_REQUESTS_PER_MIN: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MIN", "120"))
REQUEST_MAX_SIZE_BYTES: int = int(os.getenv("REQUEST_MAX_SIZE_BYTES", str(1024 * 1024)))  # 1MB limit

# ============================================================================
# Database Settings (Supabase & Postgres)
# ============================================================================
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY: str = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY", "")
).strip()
LOG_PREDICTIONS: bool = os.getenv("SUPABASE_LOG_PREDICTIONS", "true").lower() not in ("false", "0", "off")

# Logging level
LOG_LEVEL: str = os.getenv("TERRAEDGE_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()

# ============================================================================
# Phase 3 — LoRa Transport Configuration
# ============================================================================
LORA_ENABLED: bool = os.getenv("LORA_ENABLED", "false").lower() in ("true", "1", "yes")
LORA_MOCK_MODE: bool = os.getenv("LORA_MOCK_MODE", "false").lower() in ("true", "1", "yes")
LORA_SERIAL_PORT: str = os.getenv("LORA_SERIAL_PORT", "COM4")
LORA_BAUD_RATE: int = int(os.getenv("LORA_BAUD_RATE", "115200"))
LORA_FREQ_MHZ: float = float(os.getenv("LORA_FREQ_MHZ", "433.0"))
LORA_BW_KHZ: int = int(os.getenv("LORA_BW_KHZ", "125"))
LORA_SF: int = int(os.getenv("LORA_SF", "7"))
LORA_CR: str = os.getenv("LORA_CR", "4/5")
LORA_TX_POWER_DBM: int = int(os.getenv("LORA_TX_POWER_DBM", "17"))
LORA_SYNC_WORD: int = int(os.getenv("LORA_SYNC_WORD", "0x34"), 16)
LORA_CRC_ENABLED: bool = os.getenv("LORA_CRC_ENABLED", "true").lower() not in ("false", "0", "off")
LORA_ACK_ENABLED: bool = os.getenv("LORA_ACK_ENABLED", "false").lower() in ("true", "1", "yes")
LORA_ACK_TIMEOUT_MS: int = int(os.getenv("LORA_ACK_TIMEOUT_MS", "2000"))
LORA_RETRIES: int = int(os.getenv("LORA_RETRIES", "2"))
LORA_TX_INTERVAL_MS: int = int(os.getenv("LORA_TX_INTERVAL_MS", "10000"))
LORA_NODE_OFFLINE_S: int = int(os.getenv("LORA_NODE_OFFLINE_S", str(int(os.getenv("LORA_TX_INTERVAL_MS", "10000")) * 3 // 1000)))
LORA_DEDUP_CACHE_SIZE: int = int(os.getenv("LORA_DEDUP_CACHE_SIZE", "1000"))

# ============================================================================
# Phase 6 — Automated Multi-Channel Alert & Dispatch Configuration
# ============================================================================
NOTIFICATION_MODE: str = os.getenv("TERRAEDGE_NOTIFICATION_MODE", "dry_run").lower()

# SMS Channel (Twilio / Mock)
SMS_ENABLED: bool = os.getenv("SMS_ENABLED", "true").lower() not in ("false", "0", "off")
SMS_PROVIDER: str = os.getenv("SMS_PROVIDER", "mock").lower()
TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "").strip()

# Email Channel (SMTP / Mock)
EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "true").lower() not in ("false", "0", "off")
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM: str = os.getenv("SMTP_FROM", "alerts@terraedge.io").strip()
SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() not in ("false", "0", "off")

# Webhook Channel
WEBHOOK_ENABLED: bool = os.getenv("WEBHOOK_ENABLED", "true").lower() not in ("false", "0", "off")
WEBHOOK_TIMEOUT_SECONDS: float = float(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5.0"))
WEBHOOK_MAX_RETRIES: int = int(os.getenv("WEBHOOK_MAX_RETRIES", "2"))

# Common Alerting Protocol (CAP v1.2) XML Channel
CAP_ENABLED: bool = os.getenv("CAP_ENABLED", "true").lower() not in ("false", "0", "off")
CAP_SENDER: str = os.getenv("CAP_SENDER", "terraedge-gateway@emergency.gov.in").strip()
CAP_SCOPE: str = os.getenv("CAP_SCOPE", "Public").strip()

# Flood & Deduplication Settings
ALERT_DEDUP_WINDOW_SECONDS: int = int(os.getenv("ALERT_DEDUP_WINDOW_SECONDS", "300"))
ALERT_AUTO_RESOLVE_WINDOW_SECONDS: int = int(os.getenv("ALERT_AUTO_RESOLVE_WINDOW_SECONDS", "600"))

# ============================================================================
# Phase 7 — Resilient Edge Backhaul & Store-and-Forward Queue
# ============================================================================
BACKHAUL_MODE: str = os.getenv("TERRAEDGE_BACKHAUL_MODE", "live").lower()

BACKHAUL_DATA_DIR: str = os.path.join(GATEWAY_DIR, "data")
BACKHAUL_QUEUE_DB_PATH: str = os.getenv(
    "BACKHAUL_QUEUE_DB_PATH",
    os.path.join(BACKHAUL_DATA_DIR, "backhaul_queue.db")
)

BACKHAUL_SYNC_INTERVAL_S: float = float(os.getenv("BACKHAUL_SYNC_INTERVAL_S", "10.0"))
BACKHAUL_MAX_RETRIES: int = int(os.getenv("BACKHAUL_MAX_RETRIES", "5"))
BACKHAUL_PING_TIMEOUT_S: float = float(os.getenv("BACKHAUL_PING_TIMEOUT_S", "3.0"))
BACKHAUL_PRIMARY_TRANSPORT: str = os.getenv("BACKHAUL_PRIMARY_TRANSPORT", "ethernet_wifi").lower()

# Queue Maintenance & Capacity Thresholds (Phase 8)
BACKHAUL_QUEUE_RETENTION_DAYS: int = int(os.getenv("BACKHAUL_QUEUE_RETENTION_DAYS", "7"))
QUEUE_MAX_SIZE_MB: float = float(os.getenv("QUEUE_MAX_SIZE_MB", "50.0"))

# Cellular Backhaul (Modular adapter / Mock)
CELLULAR_ENABLED: bool = os.getenv("CELLULAR_ENABLED", "true").lower() in ("true", "1", "yes")
CELLULAR_MOCK_MODE: bool = os.getenv("CELLULAR_MOCK_MODE", "true").lower() in ("true", "1", "yes")
CELLULAR_PORT: str = os.getenv("CELLULAR_PORT", "COM5")
CELLULAR_APN: str = os.getenv("CELLULAR_APN", "airtelgprs.com")

# Satellite Backhaul (Modular adapter / Mock)
SATELLITE_ENABLED: bool = os.getenv("SATELLITE_ENABLED", "true").lower() in ("true", "1", "yes")
SATELLITE_MOCK_MODE: bool = os.getenv("SATELLITE_MOCK_MODE", "true").lower() in ("true", "1", "yes")
SATELLITE_PORT: str = os.getenv("SATELLITE_PORT", "COM6")


# ============================================================================
# Phase 8 — Startup Configuration Validation
# ============================================================================

def validate_configuration() -> Dict[str, Any]:
    """
    Validates gateway configuration consistency according to the current environment mode.
    Returns structured checklist with OK, WARNING, and ERROR flags.
    """
    checks = []
    warnings = []
    errors = []

    # 1. Environment mode
    checks.append({"item": "environment_mode", "status": "OK", "value": TERRAEDGE_ENV})

    # 2. Database connectivity config
    if SUPABASE_URL and SUPABASE_KEY:
        checks.append({"item": "database_config", "status": "OK", "detail": f"Supabase URL: {SUPABASE_URL}"})
    else:
        status_code = "WARNING" if TERRAEDGE_ENV in ("development", "test", "demo") else "ERROR"
        msg = "SUPABASE_URL or SUPABASE_KEY is missing (running in local in-memory fallback mode)"
        checks.append({"item": "database_config", "status": status_code, "detail": msg})
        if status_code == "ERROR":
            errors.append(msg)
        else:
            warnings.append(msg)

    # 3. Notification credentials check
    if TERRAEDGE_ENV == "production":
        if SMS_ENABLED and SMS_PROVIDER == "twilio" and not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER):
            msg = "Production mode requires TWILIO credentials when SMS_PROVIDER is 'twilio'"
            checks.append({"item": "sms_config", "status": "ERROR", "detail": msg})
            errors.append(msg)
        else:
            checks.append({"item": "sms_config", "status": "OK", "detail": f"Provider: {SMS_PROVIDER}"})

        if EMAIL_ENABLED and not (SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD):
            msg = "Production mode requires SMTP credentials when EMAIL is enabled"
            checks.append({"item": "email_config", "status": "WARNING", "detail": msg})
            warnings.append(msg)
    else:
        checks.append({"item": "notifications", "status": "OK", "detail": f"Mode: {NOTIFICATION_MODE}"})

    # 4. Backhaul adapters check
    cell_label = "MOCK (REAL HARDWARE NOT TESTED)" if CELLULAR_MOCK_MODE else f"SERIAL ({CELLULAR_PORT})"
    sat_label = "MOCK (REAL HARDWARE NOT TESTED)" if SATELLITE_MOCK_MODE else f"SERIAL ({SATELLITE_PORT})"
    checks.append({"item": "cellular_adapter", "status": "OK", "detail": cell_label})
    checks.append({"item": "satellite_adapter", "status": "OK", "detail": sat_label})

    # 5. Security token check
    if TERRAEDGE_ENV == "production" and ADMIN_TOKEN == "terraedge-admin-secret-2026":
        msg = "Production deployment should override default TERRAEDGE_ADMIN_TOKEN"
        checks.append({"item": "admin_security", "status": "WARNING", "detail": msg})
        warnings.append(msg)
    else:
        checks.append({"item": "admin_security", "status": "OK", "detail": "Configured"})

    overall = "ERROR" if errors else ("WARNING" if warnings else "OK")
    return {
        "overall_status": overall,
        "environment": TERRAEDGE_ENV,
        "gateway_id": GATEWAY_ID,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }
