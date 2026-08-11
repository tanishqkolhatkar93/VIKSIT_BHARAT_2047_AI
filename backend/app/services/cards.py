import json
import os
import sqlite3
import threading
from typing import Any

from app.core.constants import LANGUAGES


def language_name(code: str) -> str:
    for language in LANGUAGES:
        if language["code"] == code:
            return language["name"]
    return code


class CardStore:
    def __init__(self, database_url: str | None = None) -> None:
        self._lock = threading.Lock()
        self._memory: dict[str, dict[str, Any]] | None = None
        self._sqlite: sqlite3.Connection | None = None
        self._postgres_url: str | None = None

        url = database_url if database_url is not None else os.getenv("DATABASE_URL", "")
        self._configure(url)
        self._init_schema()

    def _configure(self, url: str) -> None:
        if url.startswith("sqlite:///:memory:"):
            self._sqlite = sqlite3.connect(":memory:", check_same_thread=False)
        elif url.startswith("sqlite:///"):
            import sqlite3 as _sqlite3

            path = url[len("sqlite:///"):]
            from pathlib import Path

            Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
            self._sqlite = _sqlite3.connect(path, check_same_thread=False)
        elif url.startswith("postgres") or url.startswith("postgresql"):
            self._postgres_url = url
        else:
            self._memory = {}

    def _init_schema(self) -> None:
        ddl = (
            "CREATE TABLE IF NOT EXISTS vision_cards ("
            "id TEXT PRIMARY KEY, "
            "name TEXT NOT NULL, "
            "theme TEXT NOT NULL, "
            "impact TEXT NOT NULL, "
            "quote TEXT NOT NULL, "
            "shareable_vision TEXT, "
            "tags TEXT NOT NULL, "
            "language TEXT NOT NULL, "
            "image BYTEA NOT NULL, "
            "created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        if self._sqlite is not None:
            ddl = (
                "CREATE TABLE IF NOT EXISTS vision_cards ("
                "id TEXT PRIMARY KEY, "
                "name TEXT NOT NULL, "
                "theme TEXT NOT NULL, "
                "impact TEXT NOT NULL, "
                "quote TEXT NOT NULL, "
                "shareable_vision TEXT, "
                "tags TEXT NOT NULL, "
                "language TEXT NOT NULL, "
                "image BLOB NOT NULL, "
                "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
            )
            with self._lock:
                self._sqlite.execute(ddl)
                self._sqlite.commit()
        elif self._postgres_url is not None:
            self._postgres_exec(ddl)

    def _postgres_exec(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        import psycopg

        assert self._postgres_url is not None
        with psycopg.connect(self._postgres_url) as conn:
            conn.execute(sql, params)

    def save(
        self,
        card_id: str,
        name: str,
        theme: str,
        impact: str,
        quote: str,
        shareable_vision: str | None,
        tags: list[str],
        language: str,
        image_bytes: bytes,
    ) -> None:
        if self._memory is not None:
            self._memory[card_id] = {
                "name": name,
                "theme": theme,
                "impact": impact,
                "quote": quote,
                "shareable_vision": shareable_vision,
                "tags": tags,
                "language": language,
                "image": image_bytes,
            }
            return
        payload = (
            card_id,
            name,
            theme,
            impact,
            quote,
            shareable_vision,
            json.dumps(tags),
            language,
            image_bytes,
        )
        if self._sqlite is not None:
            with self._lock:
                self._sqlite.execute(
                    "INSERT INTO vision_cards (id, name, theme, impact, quote, shareable_vision, tags, language, image) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    payload,
                )
                self._sqlite.commit()
        elif self._postgres_url is not None:
            self._postgres_exec(
                "INSERT INTO vision_cards (id, name, theme, impact, quote, shareable_vision, tags, language, image) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                payload,
            )

    def get(self, card_id: str) -> dict[str, Any] | None:
        if self._memory is not None:
            raw = self._memory.get(card_id)
            if raw is None:
                return None
            return {**raw, "id": card_id}
        if self._sqlite is not None:
            with self._lock:
                row = self._sqlite.execute(
                    "SELECT id, name, theme, impact, quote, shareable_vision, tags, language, image "
                    "FROM vision_cards WHERE id = ?",
                    (card_id,),
                ).fetchone()
            if row is None:
                return None
            return self._row_to_dict(row)
        if self._postgres_url is not None:
            import psycopg

            with psycopg.connect(self._postgres_url) as conn, conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, theme, impact, quote, shareable_vision, tags, language, image "
                    "FROM vision_cards WHERE id = %s",
                    (card_id,),
                )
                row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(row)
        return None

    @staticmethod
    def _row_to_dict(row: Any) -> dict[str, Any]:
        return {
            "id": row[0],
            "name": row[1],
            "theme": row[2],
            "impact": row[3],
            "quote": row[4],
            "shareable_vision": row[5],
            "tags": json.loads(row[6]) if row[6] else [],
            "language": row[7],
            "image": bytes(row[8]),
        }
