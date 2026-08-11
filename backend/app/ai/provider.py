import asyncio
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.schemas import VisionCard, VisionPayload

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


SYSTEM_PROMPT = """You are an optimistic but realistic AI policy and technology analyst focused on India's long-term development.
Rules:
1. Do not make up facts or statistics.
2. Do not present speculation as certainty.
3. Clearly label future scenarios, predictions and suggestions.
4. Avoid political persuasion, partisan content and inflammatory content.
5. Respect India's linguistic and cultural diversity.
6. Explain complex concepts simply.
7. Prioritize practical solutions and trade-offs.
8. Prefer retrieved sources for factual claims.
9. Never fabricate citations or claim a source was consulted if it was not retrieved.
Return valid JSON with exactly these fields and types:
{
  "vision": string,
  "opportunities": array of strings,
  "role_of_ai": string,
  "role_of_technology": string,
  "potential_impact": string,
  "challenges": array of strings,
  "action_plan": array of strings,
  "summary_2047": string,
  "fact_scenario_note": string,
  "card": {
    "theme": string,
    "beneficiaries": array of strings,
    "technology": array of strings,
    "impact": string,
    "quote": string,
    "shareableVision": string
  }
}"""


class AIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        question: str,
        language: str,
        state: str,
        category: str,
        documents: list[dict],
    ) -> VisionPayload:
        raise NotImplementedError


class LocalScenarioProvider(AIProvider):
    async def generate(
        self,
        question: str,
        language: str,
        state: str,
        category: str,
        documents: list[dict],
    ) -> VisionPayload:
        theme = _infer_theme(question, category)
        beneficiaries = _infer_beneficiaries(question)
        technologies = _infer_technologies(question, category)
        region = "India" if state == "All India" else state
        quote = _clean_quote(question)
        return VisionPayload(
            vision=(
                f"AI-generated scenario, not an official forecast: by 2047, {region} could use "
                f"{theme.lower()} and trusted public digital infrastructure to make opportunity more accessible, "
                "local services more responsive and development decisions more evidence-informed."
            ),
            opportunities=[
                f"Build local-language {theme.lower()} services that work on mobile devices.",
                "Use public-interest data systems with privacy safeguards and human review.",
                "Create district-level pilots before scaling successful models.",
                "Train youth, local institutions and small businesses to use new tools safely.",
            ],
            role_of_ai=(
                "AI can help translate information, summarize complex choices, personalize guidance, detect patterns "
                "and support faster decisions. It should assist people rather than replace accountable human judgment."
            ),
            role_of_technology=(
                "The foundation would include affordable connectivity, interoperable data platforms, secure cloud "
                "services, open standards, accessibility-first design, cyber security and local-language interfaces."
            ),
            potential_impact=(
                "The potential impact is improved access, faster service delivery and better planning. No numerical "
                "impact is stated because the retrieved sources do not verify a specific forecast for this scenario."
            ),
            challenges=[
                "Unequal digital access across regions and communities.",
                "Data quality, privacy, bias and cyber security risks.",
                "Need for long-term funding, maintenance, governance and public trust.",
                "Risk of excluding people who cannot access digital tools.",
            ],
            action_plan=[
                "Start with one high-value local problem and define measurable public outcomes.",
                "Use open, auditable safeguards for privacy, bias, safety and grievance redressal.",
                "Partner with schools, startups, civil society, local government and domain experts.",
                "Publish what works, what fails and what should be improved before scaling.",
            ],
            summary_2047=(
                f"My Viksit Bharat Vision: {quote} This is a citizen vision and AI-generated development scenario, "
                "not an official forecast."
            ),
            fact_scenario_note=(
                "Current facts are limited to the sources shown below. The 2047 pathway is an AI-generated scenario "
                "and recommendation, not a verified prediction."
            ),
            card=VisionCard(
                theme=theme,
                beneficiaries=beneficiaries,
                technology=technologies,
                impact=f"{theme} accessibility and inclusion",
                quote=quote,
                shareableVision=_shareable_vision(question),
            ),
        )


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def test_connection(self) -> dict[str, str | bool]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(endpoint)
        except httpx.TransportError:
            return {"connected": False, "message": "Network error. Could not reach the Gemini API. Check your internet connection."}

        if response.status_code in {400, 401, 403}:
            return {
                "connected": False,
                "message": "Invalid API key. Double-check the key on your Google AI Studio account.",
            }
        if response.status_code == 429:
            return {
                "connected": False,
                "message": "This API key's free quota is exhausted right now. Try again later or check your quota in Google AI Studio.",
            }
        if response.status_code >= 500:
            return {
                "connected": False,
                "message": "The Gemini API is temporarily unavailable. Please try again shortly.",
            }

        try:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return {"connected": False, "message": "Unexpected response from the Gemini API. Please try again."}

        if not models:
            return {"connected": False, "message": "The Gemini API accepted the key but returned no available models."}

        requested = f"models/{self.model}"
        active = requested if requested in models else models[0]
        return {
            "connected": True,
            "model": active.replace("models/", ""),
            "message": "API key is valid and connected.",
        }

    async def generate(
        self,
        question: str,
        language: str,
        state: str,
        category: str,
        documents: list[dict],
    ) -> VisionPayload:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        prompt = {
            "system": SYSTEM_PROMPT,
            "language": language,
            "state": state,
            "category": category,
            "question": question,
            "retrieved_documents": documents,
            "instruction": "Return only valid JSON matching the requested schema. Do not include markdown.",
        }
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=35) as client:
                    response = await client.post(
                        endpoint,
                        json={
                            "contents": [{"parts": [{"text": str(prompt)}]}],
                            "generationConfig": {"temperature": 0.45, "responseMimeType": "application/json"},
                        },
                    )
                    if response.status_code in _RETRYABLE_STATUS:
                        raise httpx.HTTPStatusError(
                            f"Upstream unavailable ({response.status_code})",
                            request=response.request,
                            response=response,
                        )
                    response.raise_for_status()
                data: dict[str, Any] = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return VisionPayload.model_validate_json(text)
            except (httpx.HTTPStatusError, httpx.TransportError, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
        raise last_exc if last_exc is not None else RuntimeError("Gemini request failed.")


def build_provider(api_key: str, model: str) -> AIProvider:
    if api_key:
        return GeminiProvider(api_key=api_key, model=model)
    return LocalScenarioProvider()


def _clean_quote(question: str) -> str:
    quote = question.strip().strip("\"'")
    if not quote.endswith("."):
        quote += "."
    return quote[:220]


def _shareable_vision(question: str) -> str:
    quote = _clean_quote(question)
    if len(quote) <= 130:
        return quote
    cut = quote[:130]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(".,;: ") + "..."


def _infer_theme(question: str, category: str) -> str:
    lower = question.lower()
    if "student" in lower or "school" in lower or "education" in lower:
        return "Education"
    if "farm" in lower or "crop" in lower or "agriculture" in lower:
        return "Agriculture"
    if "health" in lower or "hospital" in lower:
        return "Healthcare"
    return category


def _infer_beneficiaries(question: str) -> list[str]:
    lower = question.lower()
    beneficiaries = []
    if "rural" in lower:
        beneficiaries.append("Rural communities")
    if "student" in lower or "youth" in lower:
        beneficiaries.append("Youth")
    if "farmer" in lower:
        beneficiaries.append("Farmers")
    if not beneficiaries:
        beneficiaries = ["Citizens", "Local communities"]
    return beneficiaries[:3]


def _infer_technologies(question: str, category: str) -> list[str]:
    lower = question.lower()
    technologies = []
    if "ai" in lower or "artificial intelligence" in lower:
        technologies.append("AI")
    if "digital" in lower:
        technologies.append("Digital Infrastructure")
    if category in {"Technology", "Digital India"} and "Digital Infrastructure" not in technologies:
        technologies.append("Digital Infrastructure")
    if not technologies:
        technologies = ["Public Digital Infrastructure", "Data Systems"]
    return technologies[:3]
