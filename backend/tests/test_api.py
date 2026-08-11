from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vision_endpoint_returns_structured_response():
    response = client.post(
        "/api/v1/vision",
        json={
            "name": "Aarav Sharma",
            "question": "Every rural student should have access to high-quality AI-powered education.",
            "language": "en",
            "state": "All India",
            "category": "Education",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["response"]["card"]["theme"] == "Education"
    assert body["sources"]


def test_vision_rejects_unsupported_language():
    response = client.post(
        "/api/v1/vision",
        json={
            "name": "Aarav Sharma",
            "question": "How can AI support education by 2047?",
            "language": "xx",
            "state": "All India",
            "category": "Education",
        },
    )
    assert response.status_code == 400


def test_vision_with_custom_api_key_bypasses_shared_quota(monkeypatch):
    from app.api import routes
    from app.schemas import VisionCard, VisionPayload

    class StubProvider:
        async def generate(self, question, language, state, category, documents):
            return VisionPayload(
                vision="stub vision",
                opportunities=["a"],
                role_of_ai="r",
                role_of_technology="t",
                potential_impact="i",
                challenges=["c"],
                action_plan=["p"],
                summary_2047="s",
                fact_scenario_note="n",
                card=VisionCard(theme="Education", beneficiaries=["b"], technology=["x"], impact="y", quote="q"),
            )

    monkeypatch.setattr(routes, "build_provider", lambda api_key, model: StubProvider())
    routes.rate_limiter._requests.clear()
    for _ in range(50):
        routes.rate_limiter.allow("127.0.0.1")
    response = client.post(
        "/api/v1/vision",
        json={
            "name": "Aarav Sharma",
            "question": "How can India build better schools by 2047?",
            "language": "en",
            "state": "All India",
            "category": "Education",
            "api_key": "AIzaSyDummyKeyForTestingPurposeOnly",
        },
    )
    assert response.status_code == 200
    assert response.json()["response"]["card"]["theme"] == "Education"


def test_gemini_test_endpoint_validates_key(monkeypatch):
    from app.api import routes

    class StubProvider:
        async def test_connection(self):
            return {"connected": True, "model": "gemini-2.5-flash", "message": "API key is valid and connected."}

    monkeypatch.setattr(routes, "build_provider", lambda api_key, model: StubProvider())
    response = client.post("/api/v1/gemini/test", json={"api_key": "AIzaSyDummyKeyForTestingPurposeOnly"})
    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["model"] == "gemini-2.5-flash"


def test_gemini_test_endpoint_rejects_invalid_key(monkeypatch):
    from app.api import routes

    class StubProvider:
        async def test_connection(self):
            return {"connected": False, "message": "Invalid API key."}

    monkeypatch.setattr(routes, "build_provider", lambda api_key, model: StubProvider())
    response = client.post("/api/v1/gemini/test", json={"api_key": "AIzaSyDummyKeyForTestingPurposeOnly"})
    assert response.status_code == 200
    assert response.json()["connected"] is False


def _png_b64() -> str:
    import base64

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x010\x00\x00\x010\x08\x02"
        b"\x00\x00\x00\x02-\x1b\xa8\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b"
        b"\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0fIDATx\x9cc\xf8\xcf\xc0\x00\x00"
        b"\x00\x03\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return "data:image/png;base64," + base64.b64encode(png).decode()


def test_create_card_returns_public_urls():
    response = client.post(
        "/api/v1/cards",
        json={
            "name": "Priya Verma",
            "theme": "Education",
            "impact": "Every village connected to quality learning.",
            "quote": "Every child learns with AI by their side.",
            "shareableVision": "AI tutors for every child.",
            "tags": ["EDUCATION", "AI-POWERED LEARNING"],
            "language": "en",
            "image": _png_b64(),
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Priya Verma"
    assert body["share_url"].endswith(f"/c/{body['id']}")
    assert body["image_url"].endswith(f"/api/v1/cards/{body['id']}/image.png")
    assert body["share_url"].startswith("http")


def test_get_card_image_serves_png():
    created = client.post(
        "/api/v1/cards",
        json={
            "name": "Priya Verma",
            "theme": "Education",
            "impact": "Every village connected to quality learning.",
            "quote": "Every child learns with AI by their side.",
            "language": "en",
            "image": _png_b64(),
        },
    ).json()
    card_id = created["id"]

    image = client.get(f"/api/v1/cards/{card_id}/image.png")
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_public_card_page_has_open_graph_metadata():
    created = client.post(
        "/api/v1/cards",
        json={
            "name": "Priya Verma",
            "theme": "Education",
            "impact": "Every village connected to quality learning.",
            "quote": "Every child learns with AI by their side.",
            "language": "en",
            "image": _png_b64(),
        },
    ).json()
    card_id = created["id"]

    page = client.get(f"/c/{card_id}")
    assert page.status_code == 200
    html = page.text
    assert 'property="og:title"' in html
    assert 'property="og:image"' in html
    assert 'name="twitter:card" content="summary_large_image"' in html
    assert f"/api/v1/cards/{card_id}/image.png" in html


def test_missing_card_returns_404():
    assert client.get("/api/v1/cards/does-not-exist").status_code == 404
    assert client.get("/c/does-not-exist").status_code == 404
    assert client.get("/api/v1/cards/does-not-exist/image.png").status_code == 404
