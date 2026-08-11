from app.rag.retriever import KnowledgeRetriever
from app.services.cache import MemoryCache
from app.services.pulse import PulseStore
from app.services.rate_limit import RateLimiter
from app.utils.hash import hash_question, normalize_question


def test_question_hash_normalizes_question():
    assert normalize_question("  Every   Student  ") == "every student"
    assert hash_question("Every Student", "en", "All India", "Education") == hash_question(
        " every   student ", "en", "All India", "Education"
    )


def test_memory_cache_returns_value():
    cache = MemoryCache(ttl_seconds=60)
    cache.set("a", {"ok": True})
    assert cache.get("a") == {"ok": True}


def test_rate_limit_blocks_after_threshold():
    limiter = RateLimiter(limit=2)
    assert limiter.allow("ip")
    assert limiter.allow("ip")
    assert not limiter.allow("ip")


def test_retriever_returns_relevant_documents():
    retriever = KnowledgeRetriever()
    docs = retriever.search("AI education for rural students", "Education", "All India")
    assert docs
    assert any(doc["category"] == "Education" for doc in docs)


def test_pulse_store_aggregates_recorded_events():
    store = PulseStore()
    assert store.summary()["totalVisions"] == 0
    store.record("Education", "All India", "en")
    store.record("Education", "All India", "hi")
    store.record("Agriculture", "Punjab", "pa")
    summary = store.summary()
    assert summary["totalVisions"] == 3
    assert summary["popularCategories"][0] == {"name": "Education", "count": 2}
    assert summary["popularStates"][0] == {"name": "All India", "count": 2}
    assert {item["name"] for item in summary["languageDistribution"]} == {"English", "Hindi", "Punjabi"}
    assert len(summary["recentTrends"]) == 3
