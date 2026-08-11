from pathlib import Path

from fastapi.responses import HTMLResponse

from api.index import app, health, run_demo, RunRequest


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
