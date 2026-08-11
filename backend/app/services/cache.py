import json
from time import time
from typing import Any

from app.schemas import Source, VisionPayload


class MemoryCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at <= time():
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._items[key] = (time() + self.ttl_seconds, value)


class PostgresCache:
    def __init__(self, database_url: str, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._postgres_url = database_url
        self._init_schema()

    def _exec(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        import psycopg

        with psycopg.connect(self._postgres_url) as conn:
            conn.execute(sql, params)

    def _init_schema(self) -> None:
        self._exec(
            "CREATE TABLE IF NOT EXISTS vision_cache ("
            "key TEXT PRIMARY KEY, "
            "payload TEXT NOT NULL, "
            "created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )

    @staticmethod
    def _serialize(value: dict[str, Any]) -> str:
        return json.dumps(
            {
                "response": value["response"].model_dump(mode="json"),
                "sources": [source.model_dump(mode="json") for source in value["sources"]],
            }
        )

    @staticmethod
    def _deserialize(payload: str) -> dict[str, Any]:
        data = json.loads(payload)
        return {
            "response": VisionPayload.model_validate(data["response"]),
            "sources": [Source.model_validate(source) for source in data["sources"]],
        }

    def get(self, key: str) -> dict[str, Any] | None:
        import psycopg

        with psycopg.connect(self._postgres_url) as conn, conn.cursor() as cursor:
            cursor.execute(
                "SELECT payload FROM vision_cache "
                "WHERE key = %s AND created_at > now() - make_interval(secs => %s)",
                (key, self.ttl_seconds),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return self._deserialize(row[0])

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._exec(
            "INSERT INTO vision_cache (key, payload) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET payload = EXCLUDED.payload, created_at = now()",
            (key, self._serialize(value)),
        )

