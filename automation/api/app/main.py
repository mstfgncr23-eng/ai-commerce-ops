from __future__ import annotations

import json
import logging
import os

from fastapi import FastAPI, HTTPException

from .core import (
    AIEnrichment,
    ProductDecision,
    ProductInput,
    build_llm_prompt,
    decide,
    deterministic_enrichment,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ai-commerce-ops")

app = FastAPI(
    title="AI Commerce Ops",
    version="1.0.0",
    description="Structured product enrichment service for the n8n portfolio workflow.",
)


def write_audit(product: ProductInput, decision: ProductDecision) -> None:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        logger.info("audit_fallback %s", decision.model_dump_json())
        return

    try:
        import psycopg

        with psycopg.connect(database_url, connect_timeout=4) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
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
                cursor.execute(
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
                        decision.request_id,
                        product.sku,
                        json.dumps(product.model_dump()),
                        decision.model_dump_json(),
                    ),
                )
            connection.commit()
    except Exception:
        logger.exception("Audit database is unavailable; request processing continues")


def live_enrichment(product: ProductInput) -> AIEnrichment:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="AI_MODE=live requires OPENAI_API_KEY")

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        max_retries=2,
    )
    structured_model = model.with_structured_output(AIEnrichment, method="json_schema")
    result = structured_model.invoke(build_llm_prompt(product))
    if not isinstance(result, AIEnrichment):
        result = AIEnrichment.model_validate(result)
    return result


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": os.getenv("AI_MODE", "demo")}


@app.post("/enrich", response_model=ProductDecision)
def enrich(product: ProductInput) -> ProductDecision:
    mode = os.getenv("AI_MODE", "demo").strip().lower()
    if mode not in {"demo", "live"}:
        raise HTTPException(status_code=500, detail="AI_MODE must be demo or live")

    enrichment = live_enrichment(product) if mode == "live" else deterministic_enrichment(product)
    decision = decide(product, enrichment, mode=mode)
    write_audit(product, decision)
    return decision
