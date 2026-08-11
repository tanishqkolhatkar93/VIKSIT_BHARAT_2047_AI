# 🇮🇳 Viksit Bharat 2047 AI

> **Imagine India's future. Ground it in today's evidence. Share the vision.**
>
> A multilingual, RAG-powered AI platform that helps citizens explore what India could become by **2047** using retrieved official and credible Indian government sources.

[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-8E75B2)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deployed-Render-46E3B7)](https://render.com/)

---

## 🌍 What is Viksit Bharat 2047 AI?

**Viksit Bharat 2047 AI** is a full-stack web application built around a simple question:

> **What could India become by 2047?**

Citizens can ask questions about India's future in their own language, select a state/region and topic, and receive a structured AI-generated vision.

The key difference is that the system does **not rely only on an LLM's internal knowledge**.

It uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from a curated collection of **463 official and credible Indian sources**, including NITI Aayog, ministries and policy documents.

The generated response combines evidence with AI-generated reasoning and is structured into:

- 🌅 Vision narrative
- 💡 Opportunities
- 🤖 Role of AI
- 💻 Role of technology
- 📈 Potential impact
- ⚠️ Challenges
- 🛠️ Action plan
- 🇮🇳 2047 summary
- 📚 Retrieved sources

Users can then turn their vision into a **1080×1350 Vision Card**, download it as a PNG, and share it through social platforms.

The application also aggregates anonymous usage signals into an **India AI Pulse** — a live view of the topics, states and languages citizens are exploring.

---

# 🎯 Problem Statement

India's 2047 development vision spans enormous areas:

- Education
- Healthcare
- Agriculture
- Infrastructure
- Sustainability
- Technology
- Governance
- Entrepreneurship
- Employment
- Digital transformation

Citizens have questions about these areas, but the information required to understand India's possible future is often distributed across policy documents, reports and government sources.

At the same time, asking a generic LLM about India's future can produce answers that are difficult to verify and may not reflect official policy or current evidence.

### The problem

> **How can we build an AI system that allows citizens to explore India's 2047 future in a personalized, multilingual and engaging way while grounding AI-generated answers in credible Indian sources?**

---

# 💡 The Solution

Viksit Bharat 2047 AI combines:

```text
Citizen Question
       │
       ▼
Multilingual Interface
       │
       ▼
FastAPI Backend
       │
       ├── Rate Limiting
       ├── Persistent Cache
       │
       ▼
RAG Retrieval
       │
       ▼
463 Official / Credible Sources
       │
       ▼
Gemini 2.5 Flash
       │
       ▼
Structured AI Vision
       │
       ├── Opportunities
       ├── AI & Technology
       ├── Impact
       ├── Challenges
       ├── Action Plan
       └── Sources
       │
       ▼
Vision Card + India AI Pulse
```

The goal is to make AI-generated future scenarios **more grounded, accessible, multilingual and shareable**.

---

# ✨ Key Features

## 🇮🇳 1. Citizen-Powered AI Vision

Users can ask questions such as:

> "What could Maharashtra's healthcare system look like in 2047?"

or:

> "How can AI transform Indian agriculture by 2047?"

The system generates a structured vision based on retrieved evidence.

---

## 🌐 2. 11 Indian Languages

The application supports:

- 🇬🇧 English
- 🇮🇳 Hindi
- Telugu
- Tamil
- Marathi
- Bengali
- Gujarati
- Kannada
- Malayalam
- Punjabi
- Odia

The frontend uses a JSON-based internationalization system so the interface can operate across multiple Indian languages.

---

## 🔎 3. RAG-Grounded AI

Instead of sending the question directly to the LLM:

```text
Question
   ↓
Retrieve relevant evidence
   ↓
Rank documents
   ↓
Provide context to LLM
   ↓
Generate grounded response
```

The knowledge base currently contains:

> **463 official / credible Indian documents**

with metadata including:

- Category
- State
- Date
- Source URL

Sources include material from organizations such as **NITI Aayog, ministries and Indian policy documents**.

---

## 🧠 4. Gemini 2.5 Flash

The application uses:

```text
gemini-2.5-flash
```

The model receives retrieved context together with a strict structured-output prompt.

Configuration includes:

- Temperature: `0.45`
- JSON schema-based response
- Up to 3 retry attempts
- Backoff between retries
- Explicit instruction to prefer retrieved sources
- Explicit instruction not to fabricate citations

---

# 🎨 5. Vision Cards

Every generated vision can become a premium social-media-ready card.

### Card format

```text
1080 × 1350 px
```

Users can customize:

- Name
- Quote
- Theme
- Tags
- Language

The frontend renders the card as a pixel-perfect PNG using:

```text
html-to-image
```

Cards can be:

- Downloaded
- Shared
- Publicly viewed
- Used in social posts

---

# 📱 6. Social Sharing

Shareable cards are supported with public card URLs and social preview metadata.

The application generates:

- Open Graph metadata
- Twitter/X Card metadata
- Public card landing pages

Relevant routes:

```text
GET /c/{id}
GET /api/v1/cards/{id}/image.png
```

This allows a Vision Card to travel beyond the application itself.

---

# 📊 7. India AI Pulse

The project doesn't only generate AI visions.

It also asks:

> **What are citizens actually curious about?**

Anonymous analytics aggregate:

- Topic/category
- State
- Language

The resulting **India AI Pulse** provides a real-time view of collective citizen interests.

Example conceptual view:

```text
                    INDIA AI PULSE
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
    Topics              States           Languages
       │                  │                  │
 Education            Maharashtra          Hindi
 Healthcare           Karnataka            English
 Agriculture           Gujarat              Tamil
 AI & Tech             Tamil Nadu           Telugu
```

No personal identity is required for these analytics.

---

# 🔐 8. BYOK — Bring Your Own Gemini Key

Users can optionally connect their own Gemini API key.

The key:

- Is stored only in browser `localStorage`
- Is sent only over HTTPS
- Is never persisted in the database
- Is never logged
- Is never included in URLs

Using a personal key allows the user to bypass the shared free-tier generation quota and use their own Gemini quota.

---

# ⚡ 9. Rate Limiting

The default shared free-tier configuration allows:

```text
10 AI generations / rolling 24 hours / visitor
```

This helps protect the public application from uncontrolled API usage.

Users using their own Gemini key use their own quota.

---

# 🚀 10. Persistent AI Cache

Repeated questions are cached using PostgreSQL.

The cache key is derived from:

```text
question
+
language
+
state
+
category
```

Conceptually:

```text
User Question
     ↓
Normalize Inputs
     ↓
Generate Hash
     ↓
PostgreSQL Cache Lookup
     │
     ├── HIT ──→ Return cached vision
     │
     └── MISS
            ↓
          RAG
            ↓
          Gemini
            ↓
        Save result
            ↓
        Return result
```

### Why PostgreSQL instead of only memory?

The application is deployed on Render's free tier, where services can restart or spin down.

An in-memory cache would disappear.

A PostgreSQL-backed cache survives application restarts.

---

# 🏗️ Technical Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                                                             │
│  Language → State → Category → Question / Voice Input      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 REACT + TYPESCRIPT + VITE                   │
│                                                             │
│ Navbar | Vision Input | AI Response | Vision Card           │
│ Pulse Dashboard | Share Modal | Gemini Connect              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ /api/v1/*
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI                               │
│                                                             │
│ Validation → Rate Limit → Cache → RAG → AI → Response      │
└───────────────┬──────────────────────┬──────────────────────┘
                │                      │
                ▼                      ▼
┌────────────────────────┐   ┌───────────────────────────────┐
│      PostgreSQL        │   │        RAG RETRIEVER          │
│                        │   │                               │
│ vision_cache           │   │ knowledge_documents.json      │
│ vision_cards           │   │ 463 documents                │
│ pulse_events           │   │ category/state/date/URL      │
└────────────────────────┘   └───────────────┬───────────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │   GEMINI 2.5 FLASH  │
                                  │                     │
                                  │ Structured JSON     │
                                  │ + retrieved context│
                                  └──────────┬──────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │ Structured Vision   │
                                  └─────────────────────┘
```

---

# 🔄 End-to-End Request Lifecycle

When a user submits a question:

### Step 1 — Input

The user selects:

```text
Language
State / Region
Category
Name
Question
```

The question can also be entered through browser voice input.

---

### Step 2 — API Request

The frontend sends the request to:

```http
POST /api/v1/vision
```

---

### Step 3 — Validation

FastAPI + Pydantic validate the incoming request.

---

### Step 4 — Rate Limit

The system checks whether the visitor has exceeded the shared generation limit.

---

### Step 5 — Cache Lookup

The backend generates a hash from:

```text
question + language + state + category
```

If a cached result exists, it is returned immediately.

---

### Step 6 — RAG Retrieval

If there is no cache hit, the retriever searches the knowledge base.

The retrieval algorithm uses **token overlap** to rank documents according to:

- Question relevance
- Category
- State

---

### Step 7 — Context Construction

The most relevant documents are supplied to the AI provider.

---

### Step 8 — Gemini Generation

Gemini 2.5 Flash generates a structured response using a strict JSON schema.

The prompt instructs the model to:

- Prefer retrieved sources
- Ground claims in provided context
- Avoid fabricated citations
- Follow the required output structure

---

### Step 9 — Resilience

The provider retries failed Gemini requests up to **3 times with backoff**.

If no Gemini API key is configured, the application can use the clearly labeled **LocalScenarioProvider** fallback.

---

### Step 10 — Persistence

The successful response is saved in PostgreSQL's persistent cache.

---

### Step 11 — Analytics

An anonymous Pulse event is recorded for:

```text
category
state
language
```

---

### Step 12 — Frontend

The React application renders:

- Vision
- Opportunities
- AI role
- Technology role
- Impact
- Challenges
- Action plan
- 2047 summary
- Sources

---

# 🧠 RAG Architecture

The project's RAG system uses a curated JSON knowledge base:

```text
backend/app/data/knowledge_documents.json
```

Current size:

> **463 documents**

Each document contains metadata such as:

```text
Category
State
Date
URL
Content
```

### Retrieval

The current retriever uses token-overlap relevance scoring.

Conceptually:

```text
Query Tokens
      │
      ▼
Document Tokenization
      │
      ▼
Token Overlap
      │
      ├── Question relevance
      ├── Category relevance
      └── State relevance
      │
      ▼
Ranked Documents
      │
      ▼
Gemini Context
```

This keeps the system lightweight while still grounding responses in the project's curated evidence base.

---

# 🗄️ Database Architecture

The application uses **PostgreSQL through a Supabase connection pooler**.

## `pulse_events`

Stores anonymous analytics:

```text
category
state
language
```

Used by the India AI Pulse dashboard.

---

## `vision_cards`

Stores:

```text
name
theme
quote
tags
language
generated PNG image bytes
```

---

## `vision_cache`

Stores persisted AI responses using a hashed request identity.

Conceptually:

```text
Hash(
    question +
    language +
    state +
    category
)
```

This provides persistent caching across application restarts.

---

# 📡 API

## Vision

### `POST /api/v1/vision`

Generate an AI vision.

```http
POST /api/v1/vision
Content-Type: application/json
```

Returns structured vision data including:

```text
vision
opportunities
ai_role
technology_role
impact
challenges
action_plan
summary
sources
```

---

## Vision Cards

### `POST /api/v1/cards`

Creates a shareable Vision Card.

### `GET /api/v1/cards/{id}/image.png`

Returns the generated PNG image.

### `GET /c/{id}`

Returns the public shareable card landing page with social preview metadata.

---

## India AI Pulse

### `GET /api/v1/pulse`

Returns aggregated anonymous citizen-interest analytics.

---

## Gemini Connection

### `POST /api/v1/gemini/test`

Tests a user's Gemini API key without storing or exposing the key.

---

## Metadata

### `GET /api/v1/languages`

Returns supported languages.

### `GET /api/v1/states`

Returns available states/regions.

### `GET /api/v1/categories`

Returns available categories.

---

## Health

### `GET /api/v1/health`

Health-check endpoint used by deployment infrastructure.

---

# 🖥️ Frontend Architecture

Built using:

```text
React 18
TypeScript
Vite
```

Major components include:

```text
Navbar
Hero
VisionInput
AIResponse
VisionCard
ShareModal
GeminiConnectModal
PulseDashboard
Footer
```

The frontend communicates with the backend through:

```text
frontend/src/services/api.ts
```

---

# 🌐 Internationalization

The application uses a JSON-based translation system:

```text
frontend/src/utils/i18n.ts
frontend/src/locales/
```

This separates UI language content from application logic.

Supported languages:

```text
English
Hindi
Telugu
Tamil
Marathi
Bengali
Gujarati
Kannada
Malayalam
Punjabi
Odia
```

---

# 🎙️ Voice Input

The application supports browser-based speech-to-text using the **Web Speech API**.

```text
User speaks
    ↓
Browser Speech Recognition
    ↓
Text
    ↓
Vision Query
    ↓
RAG + Gemini
```

This is particularly useful for a multilingual citizen-facing application.

---

# 🐳 Deployment Architecture

The application uses a Docker multi-stage build.

```text
┌────────────────────────────┐
│ Node Build Stage            │
│                            │
│ React + Vite               │
│ npm install                │
│ npm run build              │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│ Python Runtime Stage       │
│                            │
│ FastAPI                    │
│ Static SPA                 │
│ API                        │
└──────────────┬─────────────┘
               │
               ▼
            Render
               │
               ▼
          PostgreSQL
          / Supabase
```

Deployment configuration is provided through:

```text
render.yaml
```

---

# ☁️ Production Deployment

The application is deployed on **Render**.

Health checks use:

```text
/api/v1/health
```

Environment configuration is handled using:

```text
.env
```

for local development and Render environment variables in production.

Sensitive variables are intentionally not committed to the repository.

---

# 🔐 Security & Key Hygiene

A key design principle is:

> **User API keys should never become application data.**

For BYOK:

```text
User enters Gemini key
        ↓
Browser localStorage
        ↓
HTTPS request
        ↓
Gemini
```

The key is:

- ❌ Not stored in PostgreSQL
- ❌ Not logged
- ❌ Not placed in URLs
- ❌ Not committed to Git
- ✅ Kept in browser storage
- ✅ Sent over HTTPS

Render secret variables such as the server-side Gemini key and database URL are configured outside source control.

---

# ⚡ Reliability Engineering

Several engineering decisions make the system more resilient than a simple LLM demo.

### Persistent Cache

Prevents unnecessary repeated model calls and survives service restarts.

### Retry + Backoff

Gemini calls can retry up to three times.

### Rate Limiting

Protects shared resources from uncontrolled usage.

### Local Scenario Fallback

The application can continue to demonstrate the experience when no Gemini API key is configured, with the output clearly labeled as simulated.

### Health Check

The deployment platform can verify application availability.

---

# 📈 Why RAG Instead of Pure LLM?

A pure LLM workflow would look like:

```text
Question
   ↓
LLM
   ↓
Answer
```

This project uses:

```text
Question
   ↓
Retrieve evidence
   ↓
Official / credible sources
   ↓
LLM
   ↓
Grounded answer
```

This approach is better suited to questions where **source grounding and verifiability matter**.

The system does not claim that RAG eliminates hallucinations; instead, it gives the model relevant evidence and explicitly instructs it to use retrieved sources and avoid fabricated citations.

---

# 🧪 Testing

The backend currently includes:

> **15 pytest tests**

Testing covers the application's backend behavior and core functionality.

Run:

```bash
pytest
```

Frontend quality checks include the production build and linting.

---

# 📂 Project Structure

```text
VIKSIT_BHARAT_2047_AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── routes.py
│   │   │
│   │   ├── ai/
│   │   │   └── provider.py
│   │   │
│   │   ├── rag/
│   │   │   └── retriever.py
│   │   │
│   │   ├── services/
│   │   │   ├── cache
│   │   │   ├── pulse
│   │   │   ├── cards
│   │   │   └── rate_limit
│   │   │
│   │   ├── core/
│   │   │   ├── settings
│   │   │   └── constants
│   │   │
│   │   └── data/
│   │       └── knowledge_documents.json
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar
│   │   │   ├── Hero
│   │   │   ├── VisionInput
│   │   │   ├── AIResponse
│   │   │   ├── VisionCard
│   │   │   ├── ShareModal
│   │   │   ├── GeminiConnectModal
│   │   │   ├── PulseDashboard
│   │   │   └── Footer
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │
│   │   ├── utils/
│   │   │   └── i18n.ts
│   │   │
│   │   └── locales/
│   │
│   └── dist/
│
├── Dockerfile
├── render.yaml
├── ARCHITECTURE.md
├── INTERVIEW_GUIDE.md
├── EXPLAINER.md
├── PRODUCTION_READINESS.md
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

You need:

- Python 3.x
- Node.js
- npm
- PostgreSQL / Supabase
- Gemini API key for live AI generation
- Docker (optional)

---

## 1. Clone

```bash
git clone https://github.com/tanishqkolhatkar93/VIKSIT_BHARAT_2047_AI.git
cd VIKSIT_BHARAT_2047_AI
```

---

## 2. Configure Backend

Create your backend environment configuration with the required database and Gemini settings.

Do not commit secrets.

---

## 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 4. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

---

## 5. Start Development Services

Start the FastAPI backend and React/Vite frontend using the project's development configuration.

The exact commands may vary according to the current repository scripts.

---

# 🐳 Docker

Build the production image:

```bash
docker build -t viksit-bharat-2047-ai .
```

Run:

```bash
docker run -p 8000:8000 viksit-bharat-2047-ai
```

Configure production environment variables through your deployment environment rather than hard-coding secrets into the image.

---

# 📸 Screenshots

Add screenshots here to showcase the actual product.

Recommended screenshots:

### Home / Hero

```text
![Home](assets/home.png)
```

### Multilingual Vision Input

```text
![Vision Input](assets/vision-input.png)
```

### AI Vision Result

```text
![AI Response](assets/ai-response.png)
```

### Vision Card

```text
![Vision Card](assets/vision-card.png)
```

### India AI Pulse

```text
![India AI Pulse](assets/india-ai-pulse.png)
```

---

# 🎥 Demo

Add your product demo video here:

```markdown
[▶️ Watch the Viksit Bharat 2047 AI Demo](YOUR_VIDEO_URL)
```

---

# 📊 Current Status

| Component | Status |
|---|---|
| Full-stack application | ✅ Working |
| React frontend | ✅ Working |
| FastAPI backend | ✅ Working |
| RAG knowledge base | ✅ 463 documents |
| Gemini integration | ✅ Working |
| 11 Indian languages | ✅ Supported |
| Vision Cards | ✅ Working |
| Social preview metadata | ✅ Supported |
| India AI Pulse | ✅ Working |
| PostgreSQL persistence | ✅ Implemented |
| Persistent cache | ✅ Implemented |
| Rate limiting | ✅ Implemented |
| BYOK | ✅ Implemented |
| Docker deployment | ✅ Implemented |
| Render deployment | ✅ Live |
| Backend tests | ✅ 15 passing |
| Frontend build/lint | ✅ Clean |

---

# 🧠 Engineering Highlights

This project goes beyond a basic LLM wrapper.

### 1. RAG Grounding

The LLM receives retrieved context from a curated Indian knowledge base.

### 2. Persistent Caching

PostgreSQL caching prevents repeated model calls and survives Render restarts.

### 3. Multilingual Product Design

The entire user experience is designed around 11 Indian languages.

### 4. BYOK Architecture

Users can supply their own Gemini key without the application persisting it.

### 5. Production API

FastAPI provides a modular backend with validation, rate limiting, caching and service layers.

### 6. AI + Social Product Loop

AI generation → Vision Card → Sharing → Citizen interest → India AI Pulse.

This creates a feedback loop between **individual AI exploration and collective citizen curiosity**.

---

# 🔮 Future Roadmap

Potential future improvements include:

### RAG

- [ ] Semantic/vector retrieval
- [ ] Hybrid search
- [ ] Better reranking
- [ ] Automated source ingestion
- [ ] Source freshness monitoring
- [ ] Document-level evaluation

### AI

- [ ] Multi-model support
- [ ] AI evaluation pipeline
- [ ] Hallucination detection
- [ ] Citation verification
- [ ] Agentic research workflow

### Product

- [ ] More Indian languages
- [ ] Voice output
- [ ] Personalized citizen journeys
- [ ] More advanced Pulse analytics
- [ ] Mobile application

### Infrastructure

- [ ] Background jobs
- [ ] Observability
- [ ] Structured logging
- [ ] CI/CD
- [ ] Automated security scanning
- [ ] Production-grade rate limiting

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then open a Pull Request.

When contributing, please explain:

- What problem the change solves
- What was changed
- How it was tested
- Any architectural implications

---

# 📜 License

Add the project's chosen open-source license here before publishing the repository as an officially licensed open-source project.

---

# 👨‍💻 Author

## Tanishq Kolhatkar

**Integrated M.Tech — Artificial Intelligence**

**VIT Bhopal University**

- 💻 GitHub: [tanishqkolhatkar93](https://github.com/tanishqkolhatkar93)
- 💼 LinkedIn: [Tanishq Kolhatkar](https://www.linkedin.com/in/tanishq93/)

---

# ⭐ Support the Project

If you find this project useful or interesting:

⭐ Star the repository  
🍴 Fork the project  
🐛 Open an issue  
💡 Suggest an improvement  
🤝 Contribute  

---

# 🇮🇳 The Vision

India's future will not be defined by technology alone.

It will be shaped by **what people imagine, what evidence tells us is possible, and what we choose to build today.**

Viksit Bharat 2047 AI is an experiment at that intersection:

```text
             CITIZENS
                 │
                 ▼
            QUESTIONS
                 │
                 ▼
         OFFICIAL EVIDENCE
                 │
                 ▼
                RAG
                 │
                 ▼
              AI/LLM
                 │
                 ▼
        FUTURE VISIONS
                 │
        ┌────────┴────────┐
        ▼                 ▼
  VISION CARDS       INDIA AI PULSE
        │                 │
        └────────┬────────┘
                 ▼
        COLLECTIVE FUTURE
                 │
                 ▼
        🇮🇳 VIKSIT BHARAT 2047
```

> **Don't just predict the future. Imagine it. Ground it. Share it. Build it.**

---

## 🚀 Built with AI. Grounded in Evidence. Inspired by India.

**Viksit Bharat 2047 🇮🇳**
