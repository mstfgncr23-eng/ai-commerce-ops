import json
import os
from pathlib import Path

import httpx
from fastapi.responses import HTMLResponse


# Guard against a duplicated value from bulk .env import in Vercel.
# The official API model ID is exactly `gpt-5.6-luna`.
model_value = os.getenv("OPENAI_MODEL", "").strip()
if model_value and model_value != "gpt-5.6-luna" and model_value.replace("gpt-5.6-luna", "") == "":
    os.environ["OPENAI_MODEL"] = "gpt-5.6-luna"

from api.index import app, health, run_demo, RunRequest
import api.index as api_index


# Supabase's publishable key is intentionally safe to ship in client-facing code.
# Database RLS restricts this key to INSERT-only demo audit rows whose SKU starts DEMO-.
SUPABASE_URL = "https://ahangwxrbcjxexqluyqp.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_CogFeSjaEmQNTvrw0pMlzQ_GBD0vSbJ"


def _supabase_audit(request_id, product, enrichment, approval_required):
    decision = {
        "enrichment": enrichment.model_dump(),
        "approval_required": approval_required,
    }
    payload = {
        "request_id": request_id,
        "sku": product["sku"],
        "input_payload": product,
        "decision_payload": decision,
    }
    try:
        response = httpx.post(
            f"{SUPABASE_URL}/rest/v1/product_automation_audit",
            headers={
                "apikey": SUPABASE_PUBLISHABLE_KEY,
                "Authorization": f"Bearer {SUPABASE_PUBLISHABLE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            content=json.dumps(payload),
            timeout=8.0,
        )
        return response.status_code in {200, 201, 204}
    except Exception:
        return False


# The orchestration code resolves _audit from api.index at request time.
# Patch it once at cold start so n8n and direct fallback both persist to Supabase.
api_index._audit = _supabase_audit


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def demo_home() -> HTMLResponse:
    """Serve the portfolio UI from the FastAPI entrypoint used by Vercel."""
    page = Path(__file__).with_name("index.html")
    if page.exists():
        return HTMLResponse(page.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AI Commerce Ops</h1><p>Live demo UI is unavailable.</p>", status_code=200)


# Vercel's Python routing can mount an /api function with the prefix removed.
# Keep these aliases so both routing shapes work reliably.
@app.get("/health", include_in_schema=False)
def health_alias():
    return health()


@app.post("/run", include_in_schema=False)
def run_alias(request: RunRequest):
    return run_demo(request)
