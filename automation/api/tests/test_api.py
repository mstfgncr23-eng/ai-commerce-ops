from pathlib import Path
import sys

from fastapi.testclient import TestClient


APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health_in_demo_mode(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "demo")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "demo"}


def test_ready_product_routes_to_shopify_draft(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "demo")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.post(
        "/enrich",
        json={
            "sku": "med-2048",
            "name": "Steril Prosedür Seti",
            "category_hint": "Medikal sarf malzeme",
            "stock": 84,
            "language": "tr",
            "image_ok": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sku"] == "MED-2048"
    assert body["approval_required"] is False
    assert body["action"] == "create_shopify_draft"


def test_risky_product_routes_to_human_review(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "demo")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.post(
        "/enrich",
        json={
            "sku": "med-2049",
            "name": "Kontrol Gerektiren Ürün",
            "stock": 0,
            "language": "tr",
            "image_ok": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["approval_required"] is True
    assert body["action"] == "human_review"
    assert set(body["risk_flags"]) == {"out_of_stock", "image_requires_review"}


def test_invalid_stock_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("AI_MODE", "demo")
    response = client.post(
        "/enrich",
        json={
            "sku": "med-2050",
            "name": "Hatalı Stok",
            "stock": -1,
            "language": "tr",
            "image_ok": True,
        },
    )
    assert response.status_code == 422
