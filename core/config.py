import os

# --------------------------------
# Configuration
# --------------------------------

API_URL = os.getenv("API_URL", "https://app.secoda.co/api/v1/")
API_TOKEN = os.getenv("API_TOKEN")

# Secoda integration ID for the data warehouse (used by run_sql).
# Find this in Secoda → Settings → Integrations → click your warehouse → copy the ID from the URL.
INTEGRATION_ID = os.getenv("INTEGRATION_ID")

# Base URL for endpoints outside the /api/v1/ prefix (e.g., /ai/embedded_prompt/)
_base = API_URL.rstrip("/")
EAPI_BASE_URL = _base[: -len("/api/v1")] if _base.endswith("/api/v1") else _base

