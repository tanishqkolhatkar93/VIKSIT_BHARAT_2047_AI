import base64
import html as html_module
import secrets

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response

from app.ai.provider import build_provider
from app.core.config import get_settings
from app.core.constants import CATEGORIES, LANGUAGES, STATES
from app.rag.retriever import KnowledgeRetriever
from app.schemas import (
    CreateCardRequest,
    PublicCard,
    PulseSummary,
    TestGeminiRequest,
    TestGeminiResponse,
    VisionRequest,
    VisionResponse,
)
from app.services.cache import MemoryCache, PostgresCache
from app.services.cards import CardStore
from app.services.pulse import PulseStore
from app.services.rate_limit import RateLimiter
from app.utils.hash import hash_question


settings = get_settings()
router = APIRouter(prefix="/api/v1")
public_router = APIRouter()
retriever = KnowledgeRetriever()
rate_limiter = RateLimiter(settings.rate_limit_per_day, window_seconds=86400)
pulse_store = PulseStore(settings.database_url)
card_store = CardStore(settings.database_url)

if settings.database_url.startswith("postgres"):
    cache = PostgresCache(settings.database_url, settings.cache_ttl_seconds)
else:
    cache = MemoryCache(settings.cache_ttl_seconds)


def _base_url(request: Request) -> str:
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/") + "/"
    return str(request.base_url)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "viksit-bharat-2047-ai"}


@router.get("/languages")
def get_languages() -> list[dict[str, str]]:
    return LANGUAGES


@router.get("/states")
def get_states() -> list[str]:
    return STATES


@router.get("/categories")
def get_categories() -> list[str]:
    return CATEGORIES


@router.post("/gemini/test", response_model=TestGeminiResponse)
async def test_gemini(payload: TestGeminiRequest) -> TestGeminiResponse:
    provider = build_provider(payload.api_key.strip(), settings.gemini_model)
    result = await provider.test_connection()
    return TestGeminiResponse(
        connected=bool(result["connected"]),
        model=result.get("model"),
        message=str(result["message"]),
    )


@router.get("/pulse", response_model=PulseSummary)
def get_pulse() -> PulseSummary:
    return PulseSummary(**pulse_store.summary())


@router.post("/vision", response_model=VisionResponse)
async def create_vision(payload: VisionRequest, request: Request) -> VisionResponse:
    language_codes = {language["code"] for language in LANGUAGES}
    if payload.language not in language_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported language.")
    if payload.state not in STATES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported state or region.")
    if payload.category not in CATEGORIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported category.")

    client_key = request.client.host if request.client else "anonymous"
    user_api_key = (payload.api_key or "").strip()
    if not user_api_key and not rate_limiter.allow(client_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You've reached the daily free limit of 10 AI requests. Add your own Gemini API key to keep going, or try again tomorrow.",
        )

    question_hash = hash_question(payload.question, payload.language, payload.state, payload.category)
    cached = cache.get(question_hash)
    if cached:
        pulse_store.record(payload.category, payload.state, payload.language)
        return VisionResponse(cached=True, question_hash=question_hash, **cached)

    documents = retriever.search(payload.question, payload.category, payload.state)
    active_model = (payload.model or "").strip() or settings.gemini_model
    provider = build_provider(user_api_key or settings.gemini_api_key, active_model)
    try:
        ai_response = await provider.generate(
            question=payload.question,
            language=payload.language,
            state=payload.state,
            category=payload.category,
            documents=documents,
        )
    except Exception as exc:
        if settings.environment == "development":
            raise HTTPException(status_code=502, detail=f"AI provider failed: {type(exc).__name__}") from exc
        raise HTTPException(status_code=502, detail="India AI is taking a little longer than expected. Please try again.") from exc

    sources = retriever.sources(documents)
    pulse_store.record(payload.category, payload.state, payload.language)
    cached_payload = {"response": ai_response, "sources": sources}
    cache.set(question_hash, cached_payload)
    return VisionResponse(cached=False, question_hash=question_hash, response=ai_response, sources=sources)


@router.post("/cards", response_model=PublicCard, status_code=status.HTTP_201_CREATED)
def create_card(payload: CreateCardRequest, request: Request) -> PublicCard:
    try:
        image_bytes = base64.b64decode(payload.image.split(",", 1)[-1], validate=False)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid image payload.",
        ) from exc

    if len(image_bytes) > 4_000_000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image is too large (max 4 MB).",
        )

    card_id = secrets.token_urlsafe(8)
    card_store.save(
        card_id=card_id,
        name=payload.name,
        theme=payload.theme,
        impact=payload.impact,
        quote=payload.quote,
        shareable_vision=payload.shareableVision,
        tags=payload.tags,
        language=payload.language,
        image_bytes=image_bytes,
    )
    base = _base_url(request)
    return PublicCard(
        id=card_id,
        name=payload.name,
        theme=payload.theme,
        impact=payload.impact,
        quote=payload.quote,
        shareableVision=payload.shareableVision,
        tags=payload.tags,
        language=payload.language,
        share_url=f"{base}c/{card_id}",
        image_url=f"{base}api/v1/cards/{card_id}/image.png",
    )


@router.get("/cards/{card_id}", response_model=PublicCard)
def get_card(card_id: str, request: Request) -> PublicCard:
    record = card_store.get(card_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    base = _base_url(request)
    return PublicCard(
        id=record["id"],
        name=record["name"],
        theme=record["theme"],
        impact=record["impact"],
        quote=record["quote"],
        shareableVision=record.get("shareable_vision"),
        tags=record["tags"],
        language=record["language"],
        share_url=f"{base}c/{card_id}",
        image_url=f"{base}api/v1/cards/{card_id}/image.png",
    )


@router.get("/cards/{card_id}/image.png")
def get_card_image(card_id: str) -> Response:
    record = card_store.get(card_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    return Response(
        content=record["image"],
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400", "Content-Disposition": "inline"},
    )


@public_router.get("/c/{card_id}", response_class=HTMLResponse, include_in_schema=False)
def public_card_page(card_id: str, request: Request) -> HTMLResponse:
    record = card_store.get(card_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")

    base = _base_url(request)
    image_url = f"{base}api/v1/cards/{card_id}/image.png"
    home_url = base

    name = html_module.escape(record["name"])
    quote = html_module.escape(record["quote"])
    title = html_module.escape(f"{record['name']}'s Vision for India 2047")
    description = html_module.escape(record["quote"][:160])
    page_url = html_module.escape(f"{base}c/{card_id}")
    image_secure = image_url.replace("http://", "https://")

    html = f"""<!doctype html>
<html lang="{html_module.escape(record['language'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:url" content="{page_url}">
<meta property="og:site_name" content="Viksit Bharat 2047 AI">
<meta property="og:image" content="{html_module.escape(image_url)}">
<meta property="og:image:secure_url" content="{image_secure}">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1350">
<meta property="og:image:alt" content="{title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{html_module.escape(image_url)}">
<style>
  body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:linear-gradient(160deg,#0b2545,#123e6e 55%,#7c2d12);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; color:#fff; padding:32px 16px; box-sizing:border-box; }}
  main {{ text-align:center; max-width:460px; }}
  img {{ width:100%; max-width:420px; border-radius:18px; box-shadow:0 30px 70px rgba(0,0,0,.45); }}
  blockquote {{ font-size:1.1rem; line-height:1.55; margin:24px auto; max-width:420px; color:#ffe9cc; }}
  a.cta {{ display:inline-block; margin-top:8px; padding:15px 26px; border-radius:999px; background:linear-gradient(90deg,#ff9933,#ffb43a);
    color:#0b2545; font-weight:800; text-decoration:none; box-shadow:0 14px 34px rgba(255,153,51,.35); }}
  p.note {{ margin-top:22px; font-size:.85rem; color:#bcd2ec; }}
</style>
</head>
<body>
<main>
  <img src="{html_module.escape(image_url)}" alt="{name}'s Vision for India 2047">
  <blockquote>“{quote}”</blockquote>
  <a class="cta" href="{html_module.escape(home_url)}">🇮🇳 Create Your Own Vision for India 2047</a>
  <p class="note">Viksit Bharat 2047 AI — an independent, non-government AI project.</p>
</main>
</body>
</html>"""
    return HTMLResponse(content=html)
