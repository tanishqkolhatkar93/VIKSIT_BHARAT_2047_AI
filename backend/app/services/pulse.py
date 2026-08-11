import os
import sqlite3
import threading
from collections import Counter
from pathlib import Path
from typing import Any

from app.core.constants import LANGUAGES


class PulseStore:
    def __init__(self, database_url: str | None = None, max_events: int = 5000) -> None:
        self._max_events = max_events
        self._lock = threading.Lock()
        self._memory: list[dict[str, str]] | None = None
        self._sqlite: sqlite3.Connection | None = None
        self._postgres_url: str | None = None

        url = database_url if database_url is not None else os.getenv("DATABASE_URL", "")
        self._configure(url)
        self._init_schema()

    def _configure(self, url: str) -> None:
        if url.startswith("sqlite:///:memory:"):
            self._sqlite = sqlite3.connect(":memory:", check_same_thread=False)
        elif url.startswith("sqlite:///"):
            path = url[len("sqlite:///"):]
            Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
            self._sqlite = sqlite3.connect(path, check_same_thread=False)
        elif url.startswith("postgres") or url.startswith("postgresql"):
            self._postgres_url = url
        else:
            self._memory = []

    def _init_schema(self) -> None:
        if self._sqlite is not None:
            with self._lock:
                self._sqlite.execute(
                    "CREATE TABLE IF NOT EXISTS pulse_events ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "category TEXT NOT NULL, state TEXT NOT NULL, language TEXT NOT NULL)"
                )
                self._sqlite.commit()
        elif self._postgres_url is not None:
            self._postgres_exec(
                "CREATE TABLE IF NOT EXISTS pulse_events ("
                "id BIGSERIAL PRIMARY KEY, "
                "category TEXT NOT NULL, state TEXT NOT NULL, language TEXT NOT NULL)"
            )

    def _postgres_exec(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        import psycopg

        assert self._postgres_url is not None
        with psycopg.connect(self._postgres_url) as conn:
            conn.execute(sql, params)

    def _fetch_all(self) -> list[tuple[str, str, str]]:
        if self._memory is not None:
            return [
                (event["category"], event["state"], event["language"])
                for event in self._memory
            ]
        if self._sqlite is not None:
            with self._lock:
                rows = self._sqlite.execute(
                    "SELECT category, state, language FROM pulse_events ORDER BY id"
                ).fetchall()
            return [(row[0], row[1], row[2]) for row in rows]
        if self._postgres_url is not None:
            import psycopg

            with psycopg.connect(self._postgres_url) as conn, conn.cursor() as cursor:
                cursor.execute(
                    "SELECT category, state, language FROM pulse_events ORDER BY id"
                )
                return [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        return []

    def record(self, category: str, state: str, language: str) -> None:
        if self._memory is not None:
            self._memory.append({"category": category, "state": state, "language": language})
            if len(self._memory) > self._max_events:
                self._memory.pop(0)
            return
        if self._sqlite is not None:
            with self._lock:
                self._sqlite.execute(
                    "INSERT INTO pulse_events (category, state, language) VALUES (?, ?, ?)",
                    (category, state, language),
                )
                self._sqlite.commit()
            return
        if self._postgres_url is not None:
            self._postgres_exec(
                "INSERT INTO pulse_events (category, state, language) VALUES (%s, %s, %s)",
                (category, state, language),
            )

    def summary(self, max_items: int = 5) -> dict[str, Any]:
        events = self._fetch_all()
        total = len(events)
        if total == 0:
            return {
                "totalVisions": 0,
                "popularCategories": [],
                "popularStates": [],
                "languageDistribution": [],
                "recentTrends": [],
                "message": "Not enough public responses yet.",
            }

        categories = Counter(event[0] for event in events)
        states = Counter(event[1] for event in events)
        languages = Counter(event[2] for event in events)

        language_names = {language["code"]: language["name"] for language in LANGUAGES}

        def counts(counter: Counter) -> list[dict[str, str | int]]:
            return [
                {"name": name, "count": count}
                for name, count in counter.most_common(max_items)
            ]

        return {
            "totalVisions": total,
            "popularCategories": counts(categories),
            "popularStates": counts(states),
            "languageDistribution": [
                {"name": language_names.get(code, code), "count": count}
                for code, count in languages.most_common(max_items)
            ],
            "recentTrends": [
                {"category": event[0], "state": event[1]}
                for event in reversed(events[-6:])
            ],
            "message": "",
        }
