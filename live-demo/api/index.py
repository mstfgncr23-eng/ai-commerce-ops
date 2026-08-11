from __future__ import annotations

import html
import json
import os
import time
import uuid
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="AI Commerce Ops Live Demo", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PRESETS = {
    "exam-table-paper": {
        "sku": "DEMO-ETP-001",
        "name": "Disposable Exam Table Paper",
        "supplier": "MedSupply Demo",
        "description": "Single-use examination table paper roll for clinics. Latex-free, 50 cm x 50 m.",
        "price": 249.90,
        "regulated": False,
        "risk_context": "Low-risk clinic consumable. No diagnostic or therapeutic claim.",
        "product_type": "Clinic Consumables",
    },
    "patient-monitor": {
        "sku": "DEMO-PM-001",
        "name": "Portable Patient Monitor",
        "supplier": "MedTech Demo",
        "description": "Portable multiparameter patient monitor listing ECG, SpO2, NIBP and temperature measurements.",
        "price": 18990.00,
        "regulated": True,
        "risk_context": "Medical device with diagnostic monitoring claims. Human compliance review is mandatory in this demo.",
        "product_type": "Medical Devices",
    },
    "clinic-trolley": {
        "sku": "DEMO-CT-001",
        "name": "Stainless Steel Clinic Trolley",
        "supplier": "ClinicLine Demo",
        "description": "Two-shelf stainless steel utility trolley for moving supplies inside clinics and treatment rooms.",
        "price": 3290.00,
        "regulated": False,
        "risk_context": "Clinic furniture/accessory with no medical claim.",
        "product_type": "Clinic Furniture",
    },
}

PresetName = Literal["exam-table-paper", "patient-monitor", "clinic-trolley"]


class RunRequest(BaseModel):
    preset: PresetName


class Enrichment(BaseModel):
    category: str = Field(description="Concise e-commerce category")
    seo_title: str = Field(min_length=10, max_length=70)
    seo_description: str = Field(min_length=40, max_length=180)
    normalized_description: str = Field(min_length=30, max_length=500)
    risk_score: int = Field(ge=0, le=100)
    risk_flags: list[str] = Field(default_factory=list, max_length=6)


class TraceItem(BaseModel):
    step: str
    status: Literal["success", "review", "skipped", "error"]
    duration_ms: int
    detail: str


class RunResponse(BaseModel):
    request_id: str
    orchestrator: str
    preset: str
    product: dict
    enrichment: Enrichment
    approval_required: bool
    workflow_status: str
    shopify: dict | None = None
    audit_logged: bool
    trace: list[TraceItem]


class N8nEnrichRequest(BaseModel):
    preset: PresetName


class N8nEnrichResponse(BaseModel):
    request_id: str
    preset: str
    product: dict
    enrichment: Enrichment
    approval_required: bool
    trace: list[TraceItem]


class N8nFinalizeRequest(BaseModel):
    request_id: str
    preset: PresetName
    product: dict
    enrichment: Enrichment
    approval_required: bool
    trace: list[TraceItem]


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _model_name() -> str:
    raw = _env("OPENAI_MODEL")
    # Be tolerant of accidental duplicate paste in an environment variable.
    if "gpt-5.6-luna" in raw:
        return "gpt-5.6-luna"
    return raw or "gpt-5.6-luna"


def _shop_domain() -> str:
    shop = _env("SHOPIFY_SHOP")
    if not shop:
        raise HTTPException(status_code=503, detail="SHOPIFY_SHOP is not configured")
    if shop.startswith("https://"):
        shop = shop.removeprefix("https://")
    shop = shop.rstrip("/")
    if ".myshopify.com" not in shop:
        shop = f"{shop}.myshopify.com"
    return shop


def _enrich_with_langchain(product: dict) -> Enrichment:
    if not _env("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=_model_name(), max_retries=2)
    structured = model.with_structured_output(Enrichment, method="json_schema")
    prompt = f"""
You are the AI enrichment stage inside a medical e-commerce operations workflow.
Return only the requested structured fields.

Product input:
{json.dumps(product, ensure_ascii=False, indent=2)}

Tasks:
1. Classify the product into a concise e-commerce category.
2. Produce a factual SEO title and SEO description. Do not invent certifications, approvals, clinical outcomes, warranties, or specifications.
3. Normalize the supplier description into professional product copy.
4. Assign a 0-100 operational/compliance risk score and short risk flags.
5. Treat diagnostic, therapeutic, regulated-device, prescription, or unsupported medical claims as higher risk.

This is product-content triage, not medical advice.
""".strip()
    result = structured.invoke(prompt)
    return result if isinstance(result, Enrichment) else Enrichment.model_validate(result)


def _approval_required(product: dict, enrichment: Enrichment) -> bool:
    return bool(product["regulated"] or enrichment.risk_score >= 70)


def _audit(request_id: str, product: dict, enrichment: Enrichment, approval_required: bool) -> bool:
    database_url = _env("DATABASE_URL")
    if not database_url:
        return False
    try:
        import psycopg

        with psycopg.connect(database_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS product_automation_audit (
                        request_id TEXT PRIMARY KEY,
                        sku TEXT NOT NULL,
                        input_payload JSONB NOT NULL,
                        decision_payload JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                decision = {
                    "enrichment": enrichment.model_dump(),
                    "approval_required": approval_required,
                }
                cur.execute(
                    """
                    INSERT INTO product_automation_audit
                        (request_id, sku, input_payload, decision_payload)
                    VALUES (%s, %s, %s::jsonb, %s::jsonb)
                    ON CONFLICT (request_id) DO UPDATE SET
                        input_payload = EXCLUDED.input_payload,
                        decision_payload = EXCLUDED.decision_payload,
                        updated_at = NOW()
                    """,
                    (
                        request_id,
                        product["sku"],
                        json.dumps(product),
                        json.dumps(decision),
                    ),
                )
            conn.commit()
        return True
    except Exception:
        return False


def _shopify_token() -> tuple[str, int]:
    client_id = _env("SHOPIFY_CLIENT_ID")
    client_secret = _env("SHOPIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=503, detail="Shopify client credentials are not configured"
        )
    shop = _shop_domain()
    with httpx.Client(timeout=15.0) as client:
        response = client.post(
            f"https://{shop}/admin/oauth/access_token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502, detail=f"Shopify auth failed ({response.status_code})"
        )
    body = response.json()
    token = body.get("access_token")
    if not token:
        raise HTTPException(
            status_code=502,
            detail="Shopify auth response did not include access_token",
        )
    return token, int(body.get("expires_in", 0) or 0)


def _shopify_upsert(product: dict, enrichment: Enrichment) -> dict:
    shop = _shop_domain()
    api_version = _env("SHOPIFY_API_VERSION") or "2026-07"
    access_token, expires_in = _shopify_token()
    handle = f"ai-commerce-demo-{product['sku'].lower()}"
    mutation = """
mutation UpsertDemoProduct($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
  productSet(input: $input, identifier: $identifier) {
    product { id title handle status vendor productType }
    userErrors { field message }
  }
}
""".strip()
    variables = {
        "input": {
            "title": enrichment.seo_title,
            "handle": handle,
            "descriptionHtml": f"<p>{html.escape(enrichment.normalized_description)}</p>",
            "vendor": "AI Commerce Ops Demo",
            "productType": enrichment.category or product["product_type"],
            "status": "DRAFT",
            "tags": [
                "ai-commerce-ops",
                "portfolio-demo",
                "langchain",
                "shopify-api",
                product["sku"],
            ],
            "seo": {
                "title": enrichment.seo_title,
                "description": enrichment.seo_description,
            },
        },
        "identifier": {"handle": handle},
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"https://{shop}/admin/api/{api_version}/graphql.json",
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token,
            },
            json={"query": mutation, "variables": variables},
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Shopify GraphQL HTTP error ({response.status_code})",
        )
    payload = response.json()
    if payload.get("errors"):
        raise HTTPException(
            status_code=502,
            detail={"shopify_graphql_errors": payload["errors"]},
        )
    result = payload.get("data", {}).get("productSet", {})
    if result.get("userErrors"):
        raise HTTPException(
            status_code=502,
            detail={"shopify_user_errors": result["userErrors"]},
        )
    shopify_product = result.get("product")
    if not shopify_product:
        raise HTTPException(
            status_code=502, detail="Shopify productSet returned no product"
        )
    return {
        **shopify_product,
        "token_expires_in": expires_in,
        "mode": "DRAFT_UPSERT",
    }


def _initial_enrichment(preset: PresetName) -> N8nEnrichResponse:
    request_id = str(uuid.uuid4())
    product = {**PRESETS[preset], "preset": preset}
    trace: list[TraceItem] = []

    t0 = time.perf_counter()
    trace.append(
        TraceItem(
            step="Product intake",
            status="success",
            duration_ms=max(1, int((time.perf_counter() - t0) * 1000)),
            detail=f"Validated {product['sku']}",
        )
    )

    t0 = time.perf_counter()
    enrichment = _enrich_with_langchain(product)
    trace.append(
        TraceItem(
            step="LangChain enrichment",
            status="success",
            duration_ms=int((time.perf_counter() - t0) * 1000),
            detail=f"GPT-5.6 Luna → {enrichment.category}",
        )
    )

    t0 = time.perf_counter()
    approval_required = _approval_required(product, enrichment)
    trace.append(
        TraceItem(
            step="Risk gate",
            status="review" if approval_required else "success",
            duration_ms=max(1, int((time.perf_counter() - t0) * 1000)),
            detail=f"Risk {enrichment.risk_score}/100 · "
            + (
                "human review required"
                if approval_required
                else "auto-draft allowed"
            ),
        )
    )

    return N8nEnrichResponse(
        request_id=request_id,
        preset=preset,
        product=product,
        enrichment=enrichment,
        approval_required=approval_required,
        trace=trace,
    )


def _finalize(
    *,
    request_id: str,
    preset: str,
    product: dict,
    enrichment: Enrichment,
    approval_required: bool,
    trace: list[TraceItem],
    orchestrator: str,
) -> RunResponse:
    # Re-check the decision server-side so a caller cannot bypass the risk gate.
    approval_required = _approval_required(product, enrichment)
    trace = list(trace)

    t0 = time.perf_counter()
    audit_logged = _audit(request_id, product, enrichment, approval_required)
    trace.append(
        TraceItem(
            step="PostgreSQL audit",
            status="success" if audit_logged else "skipped",
            duration_ms=max(1, int((time.perf_counter() - t0) * 1000)),
            detail="Audit row persisted"
            if audit_logged
            else "DATABASE_URL not configured; audit skipped",
        )
    )

    shopify = None
    if approval_required:
        trace.append(
            TraceItem(
                step="Shopify draft",
                status="skipped",
                duration_ms=0,
                detail="Blocked by human-in-the-loop gate",
            )
        )
        workflow_status = "pending_human_approval"
    else:
        t0 = time.perf_counter()
        shopify = _shopify_upsert(product, enrichment)
        trace.append(
            TraceItem(
                step="Shopify Admin API",
                status="success",
                duration_ms=int((time.perf_counter() - t0) * 1000),
                detail=f"DRAFT synced · {shopify['id']}",
            )
        )
        workflow_status = "shopify_draft_synced"

    return RunResponse(
        request_id=request_id,
        orchestrator=orchestrator,
        preset=preset,
        product=product,
        enrichment=enrichment,
        approval_required=approval_required,
        workflow_status=workflow_status,
        shopify=shopify,
        audit_logged=audit_logged,
        trace=trace,
    )


def _run_direct(preset: PresetName) -> RunResponse:
    enriched = _initial_enrichment(preset)
    return _finalize(
        request_id=enriched.request_id,
        preset=enriched.preset,
        product=enriched.product,
        enrichment=enriched.enrichment,
        approval_required=enriched.approval_required,
        trace=enriched.trace,
        orchestrator="direct-api-fallback",
    )


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "openai_model": _model_name(),
        "shopify_configured": bool(
            _env("SHOPIFY_CLIENT_ID")
            and _env("SHOPIFY_CLIENT_SECRET")
            and _env("SHOPIFY_SHOP")
        ),
        "database_configured": bool(_env("DATABASE_URL")),
        "n8n_webhook_configured": bool(_env("N8N_WEBHOOK_URL")),
    }


@app.post("/api/n8n/enrich", response_model=N8nEnrichResponse)
def n8n_enrich(request: N8nEnrichRequest) -> N8nEnrichResponse:
    """AI + risk stage called by the n8n Cloud workflow."""
    return _initial_enrichment(request.preset)


@app.post("/api/n8n/finalize", response_model=RunResponse)
def n8n_finalize(request: N8nFinalizeRequest) -> RunResponse:
    """Audit + Shopify stage called after n8n's branch decision."""
    return _finalize(
        request_id=request.request_id,
        preset=request.preset,
        product=request.product,
        enrichment=request.enrichment,
        approval_required=request.approval_required,
        trace=request.trace,
        orchestrator="n8n-cloud",
    )


@app.post("/api/run", response_model=RunResponse)
def run_demo(request: RunRequest) -> RunResponse:
    n8n_url = _env("N8N_WEBHOOK_URL")
    if n8n_url:
        product = {**PRESETS[request.preset], "preset": request.preset}
        try:
            with httpx.Client(timeout=55.0) as client:
                response = client.post(n8n_url, json=product)
            response.raise_for_status()
            return RunResponse.model_validate(response.json())
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"n8n orchestration failed: {type(exc).__name__}",
            ) from exc
    return _run_direct(request.preset)
