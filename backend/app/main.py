from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from app.api.routes import public_router, router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="Viksit Bharat 2047 AI API",
    description="Independent AI platform for citizen visions of India in 2047.",
    version="0.1.0",
)

allow_origins = [
    origin for origin in {settings.frontend_origin, "http://localhost:5173", settings.public_base_url} if origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), payment=()"
    return response


app.include_router(router)
app.include_router(public_router)

DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("c/"):
        raise HTTPException(status_code=404, detail="Not found.")
    file = (DIST_DIR / full_path).resolve()
    try:
        file.relative_to(DIST_DIR.resolve())
    except ValueError:
        file = DIST_DIR
    if file.is_file():
        return FileResponse(file)
    index = DIST_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return HTMLResponse(
        "Frontend build not found. Run <code>npm run build</code> inside <code>frontend/</code>.",
        status_code=503,
    )
