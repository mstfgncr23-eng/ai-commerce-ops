from pathlib import Path
import sys


APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from app.core import ProductInput, decide, deterministic_enrichment  # noqa: E402


def run() -> None:
    complete = ProductInput(
        sku="med-2048",
        name="Steril Prosedür Seti",
        category_hint="Medikal sarf malzeme",
        stock=84,
        language="tr",
        image_ok=True,
    )
    complete_decision = decide(complete, deterministic_enrichment(complete), mode="demo")
    assert complete_decision.sku == "MED-2048"
    assert complete_decision.action == "create_shopify_draft"
    assert complete_decision.approval_required is False
    assert complete_decision.confidence == 0.93

    incomplete = ProductInput(
        sku="med-2049",
        name="Kontrol Gerektiren Ürün",
        stock=0,
        language="tr",
        image_ok=False,
    )
    review_decision = decide(incomplete, deterministic_enrichment(incomplete), mode="demo")
    assert review_decision.action == "human_review"
    assert review_decision.approval_required is True
    assert "out_of_stock" in review_decision.risk_flags
    assert "image_requires_review" in review_decision.risk_flags

    print("smoke_test: ok")


if __name__ == "__main__":
    run()
