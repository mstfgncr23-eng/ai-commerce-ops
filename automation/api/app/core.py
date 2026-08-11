from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ProductInput(BaseModel):
    sku: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=180)
    category_hint: str | None = Field(default=None, max_length=120)
    stock: int = Field(ge=0, le=1_000_000)
    language: Literal["tr", "en"] = "tr"
    image_ok: bool = False
    source: str = Field(default="supplier_form", max_length=80)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()


class AIEnrichment(BaseModel):
    category: str = Field(min_length=2, max_length=100)
    seo_title: str = Field(min_length=8, max_length=180)
    seo_description: str = Field(min_length=20, max_length=600)
    confidence: float = Field(ge=0, le=1)
    risk_flags: list[str] = Field(default_factory=list, max_length=8)


class ProductDecision(AIEnrichment):
    request_id: str
    sku: str
    action: Literal["create_shopify_draft", "human_review"]
    approval_required: bool
    mode: Literal["demo", "live"]


def request_id_for(product: ProductInput) -> str:
    digest = hashlib.sha256(f"{product.sku}:{product.source}".encode("utf-8")).hexdigest()
    return f"prod_{digest[:12]}"


def deterministic_enrichment(product: ProductInput) -> AIEnrichment:
    category = product.category_hint or "Medikal sarf malzeme"
    risks: list[str] = []

    if product.stock == 0:
        risks.append("out_of_stock")
    if not product.image_ok:
        risks.append("image_requires_review")

    confidence = 0.93 - (0.18 if not product.image_ok else 0) - (0.22 if product.stock == 0 else 0)
    confidence = round(max(0.05, confidence), 2)

    if product.language == "tr":
        title = f"{product.name} — Profesyonel Kullanım"
        description = (
            f"{product.name}, medikal operasyonlarda düzenli ve güvenilir kullanım için "
            "hazırlanmış ürün çözümüdür. Teknik uygunluk ve stok durumu yayın öncesi doğrulanır."
        )
    else:
        title = f"{product.name} — Professional Use"
        description = (
            f"{product.name} is prepared for reliable use in medical operations. "
            "Technical suitability and stock status are validated before publication."
        )

    return AIEnrichment(
        category=category,
        seo_title=title,
        seo_description=description,
        confidence=confidence,
        risk_flags=risks,
    )


def decide(product: ProductInput, enrichment: AIEnrichment, mode: Literal["demo", "live"]) -> ProductDecision:
    approval_required = enrichment.confidence < 0.86 or bool(enrichment.risk_flags)
    return ProductDecision(
        **enrichment.model_dump(),
        request_id=request_id_for(product),
        sku=product.sku,
        action="human_review" if approval_required else "create_shopify_draft",
        approval_required=approval_required,
        mode=mode,
    )


def build_llm_prompt(product: ProductInput) -> str:
    return (
        "You enrich product data for a regulated medical e-commerce catalog. "
        "Do not invent certifications or clinical claims. Flag missing or risky data. "
        "Return concise SEO copy in the requested language.\n\n"
        f"Product input:\n{json.dumps(product.model_dump(), ensure_ascii=False, indent=2)}"
    )
