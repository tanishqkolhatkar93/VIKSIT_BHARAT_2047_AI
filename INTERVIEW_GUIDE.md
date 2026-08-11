# Viksit Bharat 2047 AI — Simple Project Guide

> A plain-English guide to what this project is, how it works, and how to talk about it in an interview or with anyone non-technical. Pair with `ARCHITECTURE.md` for the deep technical detail.

---

## 1. What is this project? (The 30-second elevator pitch)

**Viksit Bharat 2047 AI** is a website where any Indian citizen can type (or speak) their idea for India's future — like *"every rural student should have high-quality AI-powered education"* — and the AI:

1. Pulls in **real government reports and statistics** about India,
2. Writes a **structured 2047 vision** in the citizen's own language (11 Indian languages supported),
3. Turns it into a beautiful, **downloadable "Vision Card"** with their name and quote,
4. Gives them a **public link** they can share on WhatsApp, Facebook, X or LinkedIn — where it shows as a rich image preview.

It's an **independent, non-government AI product** — a citizen-engagement experiment inspired by the "Viksit Bharat 2047" vision, not an official government website.

**One-line summary:** *"Ask AI about India's future, grounded in real sources, and share your vision as a beautiful card."*

---

## 2. The big picture (understand this before anything else)

Think of the app as **three rooms** in one building:

```
┌──────────────────────────────────────────────────────────┐
│  ROOM 1: The Shop Window (Frontend)                      │
│  React website — what you see in the browser             │
├──────────────────────────────────────────────────────────┤
│  ROOM 2: The Kitchen (Backend)                           │
│  FastAPI server — does the real work, keeps secrets      │
├──────────────────────────────────────────────────────────┤
│  ROOM 3: The Brain (AI + RAG)                            │
│  Google Gemini + a knowledge base of 463 real documents  │
└──────────────────────────────────────────────────────────┘
```

**The golden rule of this project:** *The browser only shows things. The backend does all the smart work. The AI never makes up facts on its own — it has to read real documents first.*

---

## 3. What each piece does (simple analogies)

### Frontend — React + TypeScript (the shop window)
- A single-page app built with React (one of the most popular web frameworks).
- 11 languages: English, Hindi, Telugu, Tamil, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Odia. You click a language and the whole site switches — the translations are simple JSON files, and TypeScript **won't let a language miss a translation** (it fails to compile). That's a neat engineering trick worth mentioning.
- Voice input/output uses the **browser's built-in speech tools** — no paid AI voice service. Say your vision out loud; the AI reads the summary back.
- The Vision Card is drawn with HTML/CSS at exactly 1080×1350 (the perfect Instagram portrait size) and turned into a PNG image **in the browser** using a library called `html-to-image`. No image server needed.

### Backend — FastAPI + Python (the kitchen)
- FastAPI is a modern, fast Python web framework. Every request comes in, gets **validated** (wrong language? wrong state? rejected), then handled.
- It does three safety jobs before calling the AI:
  1. **Checks you haven't spammed** — 10 free questions per hour (rate limiting, because every AI call costs real money).
  2. **Checks if the same question was asked before** — if yes, it serves the stored answer instantly instead of calling the paid AI again (caching = speed + cost savings).
  3. **Checks the knowledge base** — pulls the most relevant real documents to ground the AI.
- It **stores** every question's topic/state/language (no personal data!) to power the **"India AI Pulse"** dashboard — "what are people asking about?".

### AI + RAG — the brain (the smart part)
- The AI model is **Google Gemini 2.5 Flash** — fast, cheap, good quality. The API key lives **only on the backend**, never in the browser (a classic security rule).
- **RAG = Retrieval-Augmented Generation.** It sounds scary; it means: *"Don't let the AI just guess. First fetch real facts, then let the AI write using those facts."*
- The knowledge base is **463 documents** built from real sources:
  - Government PDF reports (NITI Aayog, education, health, agriculture, PLFS employment surveys…)
  - World Bank statistics for India (GDP, literacy, life expectancy…)
  - Our World in Data datasets (energy, CO2, population…)
- When you ask, the backend **finds the 6 most relevant documents** (by matching words + topic + state), gives them to Gemini, and Gemini writes the vision. Then the app **shows you those sources** — so the AI can be checked. The prompt even says *"never pretend you used a source you didn't actually retrieve."* That's anti-hallucination engineering.

### The database — SQLite locally, PostgreSQL (Supabase) in production
- The code supports **three databases with zero code changes** — in-memory (tests), SQLite file (laptop), PostgreSQL (cloud). One setting (`DATABASE_URL`) switches them.
- Cloud PostgreSQL stores: the Pulse analytics events and the shared Vision Cards (so shared links keep working after the server restarts).

---

## 4. What happens when someone clicks "Generate"? (The journey)

Walk through this story — it's the clearest way to show you understand the system end-to-end:

```
1. A user types: "Every rural student should have high-quality AI education." (English, All India, Education)

2. Browser sends this to the backend.  Backend checks:
   → Is the language/state/topic allowed?      (validation)
   → Has this user hit 10 questions already?   (rate limit)
   → Has this exact question been asked today? (cache)

3. Backend searches the 463-document knowledge base → picks 6 most relevant
   documents about education/schools in India.

4. Backend builds a careful prompt: system rules + the user's question
   + those 6 documents. Sends it to Gemini (with retry if Google hiccups).

5. Gemini returns structured JSON. Backend double-checks it against a
   strict schema (Pydantic) — if malformed, it's rejected.

6. Backend saves a Pulse record (topic/state/language), stores the answer
   in cache, and sends response + source links back to the browser.

7. Browser renders the answer, speaks the summary, and draws the Vision Card.

8. User clicks "Share My Vision 🇮🇳":
   → Card image is rasterized in-browser (1080×1350 PNG)
   → PNG is uploaded to backend and stored with a random id
   → Backend returns a public link:  https://yourdomain.com/c/AbC123
   → That link opens a special page with Open Graph tags
   → WhatsApp/Facebook/X/LinkedIn crawlers read those tags and
     show a rich preview with the card image
```

**Interview gold:** if you can recite step 3 → 4 → 5 → 6 without notes, you clearly understand RAG, prompting, validation, and caching.

---

## 5. The tech stack in one breath

> *"React + TypeScript + Vite on the frontend, FastAPI + Python on the backend, Google Gemini for the AI, a lightweight RAG layer over 463 curated government/statistical documents, and SQLite locally / PostgreSQL (Supabase) in production. Tests: pytest for the backend, ESLint + TypeScript build for the frontend."*

| Layer | Technology | Why it was chosen |
|---|---|---|
| Frontend | React, TypeScript, Vite | Mainstream, typed, fast builds |
| Backend | FastAPI, Pydantic | Fast, modern, free auto-generated API docs |
| AI | Google Gemini 2.5 Flash | Fast + cheap + structured JSON output mode |
| RAG | Custom keyword retriever + JSON corpus | Zero infrastructure, explainable, testable |
| Database | SQLite → PostgreSQL (Supabase) | Same code, three backends, free cloud option |
| Card images | `html-to-image` in browser | No image server needed |
| Voice | Browser Web Speech API | Free, private, no API keys |

---

## 6. Three smart decisions you should brag about

These show engineering judgment, not just "I used a framework."

1. **"The AI never answers alone."** The system refuses to let Gemini free-wheel — it must use retrieved real documents, and its system prompt forbids inventing sources. This is the difference between a toy AI demo and an AI that can be shown to a government or public audience.

2. **"Every AI call costs money, so I engineered three shields."** Rate limiting (max 10/hour), caching identical questions (24h), and a local offline provider for testing (so developers and CI tests never spend money or depend on Google being up). Three very common interview topics solved in one design.

3. **"The whole product is one origin."** The backend serves the finished frontend website *and* the API *and* the public card pages. That single decision makes social-media image previews work with almost no extra infrastructure, and deployment becomes "deploy one thing."

Bonus smaller ones: 11 languages enforced at compile time; the card is pixel-perfect because it's just a screenshot of the real UI; voice uses the browser so there's no speech API bill.

---

## 7. Weaknesses & honest answers (interviewers love these)

Be ready to say what you'd improve — it shows maturity:

- **Retrieval is keyword-based, not semantic.** It matches words, so a paraphrase might not find the perfect document. Upgrade: embeddings + a vector database (pgvector on Supabase).
- **Cache and rate-limit are in-memory** — they reset when the server restarts, and wouldn't share across multiple server instances. Upgrade: Redis.
- **Card images are stored as blobs in the database.** Fine at small scale; at scale, move to object storage (S3/Supabase Storage).
- **Free hosting sleeps after 15 idle minutes** (Render free tier) — first visit can be slow. Upgrade: paid tier or a health-check ping.
- **Rate limiting is by IP** — people on shared mobile networks can hit the cap unfairly. Upgrade: add an optional account/email system.

---

## 8. Likely interview questions & short answers

**Q: Why FastAPI and not Flask/Django/Node?**
FastAPI is async, typed, gives automatic OpenAPI docs and Pydantic validation for free — excellent for AI APIs where the request/response contracts are strict. Python is also the natural home for AI/LLM work.

**Q: How does your RAG work?**
Offline, I built a corpus of 463 documents from government PDFs and World Bank/OWiD statistics. At request time, I tokenize the question, score every document by word overlap + category match + state match, take the top 6, and inject them into the Gemini prompt. Then I show the user those exact sources. It's deterministic and testable.

**Q: How do you prevent the AI from hallucinating?**
Three layers: (1) retrieval-first grounding — facts must come from retrieved docs; (2) a system prompt rule that says never fabricate citations and never claim a source wasn't consulted; (3) a visible "fact vs scenario" disclaimer and source list in the UI. I also validate the model's JSON output with Pydantic so a malformed answer is rejected rather than rendered.

**Q: How do you handle cost and abuse?**
Rate limit of 10 requests/hour per IP, a 24-hour cache so identical questions never re-hit the paid model, small prompt budgets (max 800 chars input, 6 docs), and a local fallback provider for dev/CI so testing costs nothing.

**Q: How is the AI key kept safe?**
It lives only in backend environment variables. The frontend never talks to Gemini directly — it talks to my FastAPI backend, which holds the key. The built website contains no secret.

**Q: Why one server instead of separate frontend/backend deploys?**
A single FastAPI service serves the built React app, the API, and the `/c/:id` public card pages. Social-media crawlers need a single public origin to fetch card previews; one origin also simplifies CORS and deployment.

**Q: What was the hardest bug you solved?**
Google's Gemini endpoint occasionally returns transient "endpoint unavailable" errors. I added a 3-attempt retry with exponential backoff on retryable status codes (429/5xx), which turned random user-facing failures into transparent retries.

**Q: How do you test an app that calls a paid AI?**
I made the AI provider an interface with two implementations — real Gemini and a deterministic local one. Tests use the local one, so CI runs in under a second, costs nothing, and is 100% reproducible.

**Q: How would you scale this?**
Move retrieval to embeddings + pgvector for semantic search, move cache/rate-limit to Redis, move card images to object storage, and deploy multiple instances behind a load balancer. The code is already shaped for it — stores are abstracted behind interfaces.

---

## 9. Demo day talking points (for showing it to anyone)

1. **Start with the topic dropdowns** — "Anyone can pick any Indian state and any topic."
2. **Type a vision** — read it aloud, like a citizen would.
3. **Generate** — point out the sources section: *"See these? The AI had to read these real reports before answering."*
4. **Download the card** — *"This is generated right in the browser, no image server."*
5. **Share** — open the WhatsApp option, or click "Challenge Your Friends." Explain the public link + image preview.
6. **Switch to Hindi** — the whole UI flips, and Gemini answers in Hindi too.
7. **Talk into the mic** — voice input works in Chrome/Edge/Safari.
8. **Scroll to India AI Pulse** — "Here's what India is asking about, live, anonymously."

---

## 10. One-paragraph closing statement (memorize this)

> "Viksit Bharat 2047 AI is a full-stack AI product that lets citizens envision India's future. The frontend is React + TypeScript with 11 languages and browser-native voice. The backend is FastAPI with rate limiting, caching, and structured validation. The core innovation is a RAG pipeline: I built a 463-document knowledge base from government and statistical sources, retrieve the top relevant documents for each question, and ground Gemini's answer in them — with anti-hallucination rules and visible citations. Users can turn their answer into a shareable 1080×1350 Vision Card with a public link that renders rich previews on WhatsApp, Facebook, X, and LinkedIn. It runs on one deployable origin, stores data in PostgreSQL via Supabase, and is built so that testing never costs money by swapping the AI provider for a deterministic local fallback."

---

*Want the deep technical version? See `ARCHITECTURE.md` in the project root.*
