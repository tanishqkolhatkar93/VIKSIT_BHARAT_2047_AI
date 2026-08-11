# Viksit Bharat 2047 AI — Production-Grade Readiness

> This document explains *why* this project is designed and shipped as a production-grade application, and backs every claim with the exact code location. It is written for engineers, reviewers, and anyone evaluating whether this codebase is production-ready — not just a demo.

---

## Table of Contents

1. [The Production Mindset](#1-the-production-mindset)
2. [Security](#2-security)
3. [Reliability & Resilience](#3-reliability--resilience)
4. [Performance & Cost Control](#4-performance--cost-control)
5. [Data Integrity & Validation](#5-data-integrity--validation)
6. [Testability & CI](#6-testability--ci)
7. [Operability & 12-Factor Compliance](#7-operability--12-factor-compliance)
8. [Deployment Automation](#8-deployment-automation)
9. [Scalability by Design](#9-scalability-by-design)
10. [Observability](#10-observability)
11. [Honest Gaps & Remediation Plan](#11-honest-gaps--remediation-plan)
12. [Production Checklist](#12-production-checklist)

---

## 1. The Production Mindset

A production-grade app is not defined by any single feature. It is defined by how it answers six questions:

| Question | This project's answer |
|---|---|
| What if the AI provider is down? | Retry with backoff, timeout bounds, graceful 502 |
| What if users abuse it? | Rate limiting, input validation, cost caps |
| What if secrets leak? | Backend-only keys, gitignored env files, no PII stored |
| What if the same question is asked twice? | 24h normalized cache → instant, zero-cost replies |
| How do we prove it works? | 17 automated tests that never call a paid API |
| How do we ship it? | Docker multi-stage build + Render blueprint, auto-deploy |

The entire codebase was built around these answers, not as an afterthought.

---

## 2. Security

### 2.1 Secrets never reach the browser

The Gemini API key exists **only** in backend environment variables (`app/core/config.py:9`). The frontend talks to the FastAPI backend, which alone holds the key (`frontend/src/services/api.ts:3` uses a same-origin `/api` base URL). The built SPA bundle contains no secret. Verified by a static audit of the production build.

### 2.2 No PII, no stored questions

- The only identifying field is a **display name** chosen by the user (`schemas.py:14`).
- The user's question text is **never persisted**. Only a normalized **SHA-256 hash** is used as a cache key (`utils/hash.py:9`), making the stored data useless if the database leaks.
- There is no email, phone, address, or analytics cookie.

### 2.3 Defense-in-depth HTTP hardening (`app/main.py`)

- **CORS allowlist** built only from configured origins: `FRONTEND_ORIGIN`, localhost dev, and `PUBLIC_BASE_URL` (`main.py:19-29`).
- **Security headers** applied on every response (`main.py:33-39`):
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY` (blocks clickjacking)
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), geolocation=(), payment=()`
- **Path-traversal guard** in the static file server — resolved paths are validated against the allowed `DIST_DIR` before serving (`main.py:52-56`).

### 2.4 Input validation on every boundary

- **Server-side**: Pydantic models with length constraints (`schemas.py`), plus whitelist checks for language/state/category before any work happens (`routes.py:69-75`). Unsupported values get 400, malformed payloads get 422.
- **Client-side**: TypeScript types mirror the contracts exactly (`frontend/src/types/api.ts`), and the form disables submission until inputs are valid (`VisionInput.tsx:35`).
- **Binary uploads**: card images must decode as PNG and are rejected at >4 MB (413) or on invalid payload (422) (`routes.py:114-126`).

### 2.5 Injection & XSS protection

- **Prompt injection is bounded**: all user content enters the LLM prompt as *data*; the prompt contract and JSON-mode output keep the model from escaping its schema (`provider.py:141-161`).
- **Reflected content is HTML-escaped** on the public card page (`routes.py:193-196`), preventing stored/reflected XSS on `/c/{id}`.
- **Anti-fabrication rule** in the system prompt: *"Never fabricate citations or claim a source was consulted if it was not retrieved"* (`provider.py:22`).

### 2.6 Repo hygiene

`.env` and `.env.*` are gitignored (`.gitignore:1-3`); only `.env.example` is committed with placeholder values. Secrets never enter git history.

---

## 3. Reliability & Resilience

### 3.1 The AI provider is treated as an unreliable dependency

Production LLM APIs are flaky. The `GeminiProvider` handles this explicitly (`app/ai/provider.py:153-178`):

- **3 attempts** with linear backoff (`1.5s`, `3s`).
- Retries only on **retryable statuses** `{429, 500, 502, 503, 504}` and transport errors — a 400/401 fails fast (no wasted retries).
- **35-second timeout** on every attempt so a hung upstream can't hang the user.

This was added in response to a real incident where Google returned transient `Endpoint unavailable` errors — turning random failures into automatic retries.

### 3.2 Graceful failure, not stack traces

- Non-2xx upstream responses raise typed `HTTPStatusError`, mapped in the route layer (`routes.py:100-103`).
- In production, users see a **safe generic message**; detailed exception types are exposed only in `development` (`ENVIRONMENT` setting). No internals leak.

### 3.3 The app can run with zero external dependencies

If `GEMINI_API_KEY` is absent, `build_provider()` returns a deterministic `LocalScenarioProvider` (`provider.py:181-184`). The site still works — dev environments and CI never depend on Google being up, and never spend money.

### 3.4 Database portability

`PulseStore` and `CardStore` support **PostgreSQL, SQLite, and in-memory** via one `DATABASE_URL` (`services/pulse.py:24-33`, `services/cards.py:28-42`). Local dev and tests run on SQLite/memory; production runs on Supabase Postgres — same code, no drift between environments.

### 3.5 Liveness

`GET /api/v1/health` returns `200` and is used as Render's health-check path (`render.yaml`).

---

## 4. Performance & Cost Control

Every LLM call costs money and latency. The app has four engineered shields:

### 4.1 Response caching
Identical questions are answered from a **24-hour TTL cache** (`config.py:13`, `services/cache.py`). Cache keys are SHA-256 of the *normalized* question + dimensions (`utils/hash.py`), so "  Every   Student " and "every student" hit the same entry. Cached hits skip the LLM entirely (`routes.py:84-88`) → **instant responses, zero cost**.

### 4.2 Rate limiting
A sliding-window limiter caps each client at **10 requests/hour** (`services/rate_limit.py`, `routes.py:77-82`) — bounding worst-case spend and abuse.

### 4.3 Prompt budget control
- Question capped at 800 chars (`schemas.py:15`).
- Retrieval capped at **6 documents** (`retriever.py:22`).
- Quote truncated to 220 chars before rendering (`VisionCard.tsx`).
- `temperature 0.45` + `responseMimeType: application/json` (`provider.py:161`) → high first-pass schema compliance, fewer re-renders.

### 4.4 Lean frontend
The React build ships as **264 KB JS (83.5 KB gzip)** + 11.6 KB CSS — a single same-origin bundle with no external CDN round-trips (`frontend/dist`). Serving the SPA from the API origin eliminates CORS latency and a second infrastructure dependency.

### 4.5 Cache performance
Cache + rate limiter are O(1) amortized in-memory structures (`services/cache.py`, `services/rate_limit.py`) — no per-request I/O on the hot path.

---

## 5. Data Integrity & Validation

### 5.1 The AI's output is a contract, not a suggestion

Gemini is instructed to return JSON (`responseMimeType`), and the response is **re-validated with Pydantic** (`VisionPayload.model_validate_json`, `provider.py:173`). Malformed or missing fields are rejected before they reach the user — the frontend never renders unvalidated AI output.

### 5.2 Strong typing end-to-end

- Every endpoint declares `response_model=` (e.g., `routes.py:67,112,155`), so FastAPI validates/coerces the wire format automatically.
- Frontend mirrors every contract in `frontend/src/types/api.ts`.
- The i18n system makes `Dictionary = typeof en` (`utils/i18n.ts:16`), so a missing translation key in **any of the 11 languages is a compile-time error** — it is impossible to ship an untranslated UI.

### 5.3 Persistence with schema

Both persistent stores create explicit schemas idempotently at startup (`pulse.py:36-49`, `cards.py:44-76`), and Postgres DDL uses proper types (`BIGSERIAL`, `BYTEA`, `TIMESTAMPTZ`). Supabase additionally provides managed backups for the production database.

---

## 6. Testability & CI

### 6.1 A test suite that runs for free and never flakes

| Suite | Coverage |
|---|---|
| `tests/test_api.py` (12 tests) | Health, vision flow, input rejection, card URL construction, PNG serving, Open Graph metadata, 404 behavior |
| `tests/test_core.py` (5 tests) | Hash normalization, cache, rate limiter, retriever relevance, pulse aggregation |

- `conftest.py` forces `DATABASE_URL=sqlite:///:memory:` → tests are **hermetic** (no real DB).
- The deterministic `LocalScenarioProvider` means **tests never call a paid API**, run in <1s, and are reproducible anywhere.

### 6.2 Frontend gates

`npm run lint` (ESLint + typescript-eslint) and `npm run build` (`tsc -b` type-check + Vite) are required to pass — type errors and unused variables block the build, and the whole 11-language i18n tree is type-checked.

### 6.3 Verified container

The Docker image was built and smoke-tested locally before push: health `200`, SPA `200`, API routes working, and API 404s correctly *not* masked by the SPA fallback (`main.py:50-51`).

---

## 7. Operability & 12-Factor Compliance

The codebase follows 12-Factor principles:

| Principle | Evidence |
|---|---|
| **Config in environment** | All settings via `pydantic-settings` from env / `.env` (`config.py:6-21`) |
| **Backing services as resources** | Database chosen by `DATABASE_URL`, AI by `GEMINI_API_KEY` |
| **Disposability** | Stateless except DB; stores re-create schema at boot; container starts cleanly |
| **Dev/prod parity** | Same code paths; only env differs (SQLite ↔ Postgres, fallback ↔ Gemini) |
| **Logs to stdout** | Uvicorn logs to stdout; `PYTHONUNBUFFERED=1` in container |
| **Build/release/run separation** | Docker image is the immutable artifact; env vars configure the release |

The backend also serves the **built frontend itself** (`main.py:48-65`), so the entire product is one deployable unit — fewer moving parts, one place to roll back, no version-skew between SPA and API.

---

## 8. Deployment Automation

- **Dockerfile** — multi-stage build: stage 1 compiles the React app (`node:20-alpine`), stage 2 installs pinned Python deps and serves everything with `uvicorn` (`python:3.12-slim`). Reproducible from `requirements.txt` + `package-lock.json`.
- **`.dockerignore`** — excludes `.git`, secrets, 173 MB of raw RAG data, node_modules, and build output → small, fast, safe build context.
- **`render.yaml`** — infrastructure-as-code: service definition, Docker runtime, free tier, region, health-check path, auto-deploy on push, and env var scaffold (secrets marked `sync: false` so they must be set explicitly in the dashboard).
- **Health check** — `/api/v1/health` gated; Render restarts the instance if it fails.

---

## 9. Scalability by Design

The architecture anticipates growth without a rewrite:

1. **Store abstraction** → move from Supabase Postgres to any Postgres-compatible service is a URL change.
2. **Deterministic retriever** → plug-in semantic search (pgvector) behind the same `KnowledgeRetriever` interface (`retriever.py`).
3. **In-memory cache/limiter** → swap for Redis-backed implementations; call sites don't change.
4. **Card PNGs in DB** → move to object storage (S3/Supabase Storage); the `PublicCard` contract already returns absolute `image_url`s.
5. **Single origin** → the SPA + API + card pages share one domain, so horizontal scaling is a matter of adding instances behind a load balancer.

---

## 10. Observability

Current state:
- **Liveness**: `/api/v1/health`.
- **Product analytics**: anonymous `pulse_events` aggregate on `/api/v1/pulse`.
- **Container logs**: uvicorn access/error logs to stdout (captured by Render).

Gaps being tracked (see §11): structured request logs with latency/token/retry telemetry, error tracking (Sentry), and uptime monitoring for the free-tier instance.

---

## 11. Honest Gaps & Remediation Plan

Production-grade means being honest about what is *not* yet in place. These are scoped, with concrete fixes:

| Gap | Impact today | Remediation |
|---|---|---|
| In-memory cache & rate limiter | State resets on restart; not shared across instances | Redis-backed implementations (interface already isolated) |
| Keyword-only retrieval | Paraphrases may miss relevant docs | pgvector embeddings + hybrid (vector + keyword) search |
| Card PNGs in `BYTEA` | Larger DB; fine at MVP scale | Move to object storage; keep URL contract |
| No structured request logging / metrics | Debugging is via uvicorn logs | JSON structured logs + latency/token/retry telemetry |
| No error tracker | Production bugs rely on logs | Sentry integration in `routes.py` exception paths |
| IP-based rate limit | Shared-NAT users share the quota | Optional auth/quota system |
| Free-tier cold start | ~30s wake after 15-min idle | Uptime pinger or paid tier |

None of these are architectural blockers — each is an isolated swap behind an existing interface.

---

## 12. Production Checklist

| Area | Status | Evidence |
|---|---|---|
| Secrets never in client | ✅ | Backend-only `GEMINI_API_KEY` (`config.py`) |
| No PII / data minimization | ✅ | Hash-only cache keys (`utils/hash.py`) |
| Input validation (server + client) | ✅ | Pydantic + whitelists (`routes.py:69-75`) |
| Output schema validation | ✅ | `model_validate_json` (`provider.py:173`) |
| Security headers + CORS allowlist | ✅ | `main.py:19-39` |
| XSS / HTML escaping | ✅ | `routes.py:193-196` |
| Path traversal protection | ✅ | `main.py:52-56` |
| Rate limiting | ✅ | `services/rate_limit.py` |
| Caching for cost/latency | ✅ | `services/cache.py` + 24h TTL |
| Upstream retry + timeout | ✅ | `provider.py:153-178` |
| Safe prod error messages | ✅ | `routes.py:100-103` |
| Health check | ✅ | `/api/v1/health` + `render.yaml` |
| Automated tests (hermetic, free) | ✅ | 17 tests, in-memory DB, local provider |
| Type-safe build gates | ✅ | `tsc -b`, ESLint, `Dictionary = typeof en` |
| Reproducible deployment | ✅ | Multi-stage Dockerfile + `render.yaml` |
| Production DB persistence | ✅ | Supabase Postgres via `DATABASE_URL` |
| Structured logging / monitoring | ⏳ Planned | §11 remediation |
| Error tracking | ⏳ Planned | §11 remediation |
| Distributed cache | ⏳ Planned | §11 remediation |
| Semantic retrieval | ⏳ Planned | §11 remediation |

---

## Closing Statement

> *This application is production-grade because every external risk — a flaky AI provider, abuse, cost overruns, secret leakage, malformed AI output, and environment drift — was identified and engineered around from the start. It ships as a single immutable container with hermetic, free tests, 12-factor configuration, defense-in-depth security, and a persistence layer that runs identically on a laptop and in the cloud. The remaining gaps are not architectural debt; they are isolated, interface-backed swaps with a written remediation plan.*

---

*Companion docs: `ARCHITECTURE.md` (deep technical), `INTERVIEW_GUIDE.md` (interview prep), `EXPLAINER.md` (plain language).*
