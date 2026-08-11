# Project Summary — "Viksit Bharat 2047 AI"

> A full-stack web application where Indian citizens ask AI about India's future by 2047,
> grounded in official government sources, available in 11 Indian languages, with shareable
> Vision Cards and a live crowd-sourced "India AI Pulse".

---

## What the project is

A **full-stack web application** where Indian citizens (and anyone curious about India's future) ask AI questions about what India could become by **2047** — the "Viksit Bharat" (Developed India) vision. Users type or speak a question in their own language, and the app generates a structured, optimistic-but-realistic AI vision built from **retrieved official government documents (RAG)**, not just the model's imagination.

Each answer includes: a narrative vision, opportunities, the role of AI, the role of technology, potential impact, challenges, an action plan, and a 2047 summary. Users can then create a **premium 1080×1350 "Vision Card"** (with their name, quote, theme, tags) that can be downloaded as PNG or shared on WhatsApp, Facebook, LinkedIn, X, and Instagram with proper social-media preview metadata (Open Graph + Twitter Cards).

The app also aggregates anonymous analytics ("India AI Pulse") showing what topics/states/languages people care about most — a live, real-time view of collective citizen priorities.

---

## Tech stack & architecture

### Frontend — React 18 + TypeScript + Vite

- Fully translated into **11 Indian languages** (English, Hindi, Telugu, Tamil, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Odia) via a JSON-based i18n system
- Voice input through the browser Web Speech API (speech → text)
- Vision Card rendered as pixel-perfect PNG via `html-to-image`, with download + share flows
- Clean, premium UI with glassmorphism modal for connecting a personal Gemini API key
- Navbar status indicator for AI connection state

### Backend — FastAPI (Python) + httpx + Pydantic

- `POST /api/v1/vision` — main AI endpoint: validates input → rate-limits → checks a Postgres-persisted cache → retrieves relevant documents (RAG) → calls Google Gemini → returns structured JSON
- `POST /api/v1/cards` + `GET /api/v1/cards/{id}/image.png` + `GET /c/{id}` — shareable card creation, PNG serving, and public Open Graph landing page
- `GET /api/v1/pulse` — aggregates anonymous analytics
- `POST /api/v1/gemini/test` — validates a user's own API key without exposing or storing it
- `GET /api/v1/languages | states | categories` — dynamic dropdowns
- Modular layout: `app/ai` (provider), `app/rag` (retriever), `app/services` (cache, pulse, cards, rate-limit), `app/api` (routes), `app/core` (config/constants)

### AI pipeline (RAG)

- 463 documents indexed from official/credible Indian sources (NITI Aayog, ministries, policy documents) stored in `knowledge_documents.json` with category/state/date/URL metadata
- Token-overlap retrieval ranks documents by relevance to the question + category + state
- Gemini 2.5 Flash (`gemini-2.5-flash`) with a strict JSON schema prompt, temperature 0.45, retry logic (3 attempts with backoff) for resilience
- The prompt explicitly instructs the model to prefer retrieved sources and never fabricate citations

### Database — PostgreSQL (via Supabase connection pooler)

- `pulse_events` — anonymous analytics (category, state, language) for the Pulse dashboard
- `vision_cards` — name, theme, quote, tags, language, and the generated PNG image bytes
- `vision_cache` — **persisted AI responses keyed by a hash** of question+language+state+category, so repeat questions are served instantly and survive restarts (crucial on Render's free tier which spins down)

### Rate limiting & BYOK (bring-your-own-key)

- Free-tier default: **10 AI generations per day** per visitor (rolling 24h window)
- Users can connect their **own Gemini API key** via a polished modal → it bypasses the shared daily quota (they use their own quota)
- Key is stored only in the user's browser localStorage, sent only via HTTPS, never persisted in the database, never logged

### Deployment

- Docker multi-stage build (Node builds the frontend → Python image runs FastAPI serving both API + static SPA)
- Deployed on **Render** (free tier) via `render.yaml` blueprint, health-checked at `/api/v1/health`
- Environment config via pydantic-settings (`.env` / Render env vars)

---

## Project structure

```
backend/
  app/
    main.py            # FastAPI app + SPA static serving + CORS
    api/routes.py      # all API endpoints
    ai/provider.py     # Gemini provider + LocalScenario fallback + connection test
    rag/retriever.py   # knowledge document retrieval
    services/          # cache (Postgres/Memory), pulse, cards, rate_limit
    core/              # settings, constants
    data/              # knowledge_documents.json (463 docs)
  tests/               # 15 pytest tests
frontend/
  src/
    components/        # Navbar, Hero, VisionInput, AIResponse, VisionCard, ShareModal, GeminiConnectModal, PulseDashboard, Footer
    services/api.ts    # typed API client
    utils/i18n.ts      # 11-language dictionary system
    locales/           # per-language JSON
  dist/                # production build served by FastAPI
Dockerfile / render.yaml
ARCHITECTURE.md / INTERVIEW_GUIDE.md / EXPLAINER.md / PRODUCTION_READINESS.md
```

---

## Key user flow

1. User picks language, state/region, topic, enters name + question (or speaks it)
2. Backend validates → rate-limits → checks cache → retrieves relevant docs → Gemini generates a structured vision
3. AI response displayed in the chosen language with sources cited
4. User creates a **Vision Card** (auto-generates theme, quote, tags)
5. Card downloadable as PNG / shareable with social preview links
6. Every generation updates the anonymous **India AI Pulse** analytics

---

## Notable engineering decisions

- **Postgres-persisted cache** instead of in-memory — works around Render free-tier restarts/spin-down
- **Same-origin API calls in production** — SPA served by FastAPI calls relative `/api/v1/*`, no CORS issues in prod
- **RAG over pure LLM** — grounded answers with verifiable official sources
- **`sync:false` env vars on Render** — secrets (Gemini key, DB URL) entered manually, never committed
- **LocalScenarioProvider fallback** — app still answers (with clearly-labeled simulated scenarios) when no API key is configured
- **Careful key hygiene** — user API keys never touch logs, DB, or URLs

---

## Current status

- Fully working locally (15 backend tests passing, frontend build + lint clean)
- **Deployed on Render** (free tier) with a live URL
- Production-grade docs included: architecture, interview guide, plain-English explainer, production-readiness assessment

---

## Highlights for a LinkedIn post

- Citizen-powered AI vision for India 2047
- 11 Indian languages
- Grounded in official government sources (RAG)
- Shareable branded vision cards with real social previews
- Live crowd-sourced "India AI Pulse"
- Free-tier friendly with BYOK (bring-your-own-key)
- Deployed to production (Docker + Render)
- Full-stack journey: idea → architecture → deployment
