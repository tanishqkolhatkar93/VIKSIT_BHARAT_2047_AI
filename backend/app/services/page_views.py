import os
import sqlite3
import threading
from datetime import date
from typing import Any

from app.schemas import AnalyticsSummary


class PageViewStore:
    def __init__(self, database_url: str | None = None, max_events: int = 20000) -> None:
        self._max_events = max_events
        self._lock = threading.Lock()
        self._memory: list[tuple[str, str]] | None = None
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

            from pathlib import Path

            path = url[len("sqlite:///"):]
            Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
            self._sqlite = _sqlite3.connect(path, check_same_thread=False)
        elif url.startswith("postgres") or url.startswith("postgresql"):
            self._postgres_url = url
        else:
            self._memory = []

    def _init_schema(self) -> None:
        if self._sqlite is not None:
            with self._lock:
                self._sqlite.execute(
                    "CREATE TABLE IF NOT EXISTS page_views ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "visitor_id TEXT NOT NULL, "
                    "page TEXT NOT NULL DEFAULT '/', "
                    "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
                )
                self._sqlite.commit()
        elif self._postgres_url is not None:
            self._postgres_exec(
                "CREATE TABLE IF NOT EXISTS page_views ("
                "id BIGSERIAL PRIMARY KEY, "
                "visitor_id TEXT NOT NULL, "
                "page TEXT NOT NULL DEFAULT '/', "
                "created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )

    def _postgres_exec(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        import psycopg

        assert self._postgres_url is not None
        with psycopg.connect(self._postgres_url) as conn:
            conn.execute(sql, params)

    def record(self, visitor_id: str, page: str = "/") -> None:
        page = (page or "/")[:200]
        if self._memory is not None:
            self._memory.append((visitor_id, page))
            if len(self._memory) > self._max_events:
                self._memory.pop(0)
            return
        if self._sqlite is not None:
            with self._lock:
                self._sqlite.execute(
                    "INSERT INTO page_views (visitor_id, page) VALUES (?, ?)",
                    (visitor_id, page),
                )
                self._sqlite.commit()
            return
        if self._postgres_url is not None:
            self._postgres_exec(
                "INSERT INTO page_views (visitor_id, page) VALUES (%s, %s)",
                (visitor_id, page),
            )

    def _fetch_all(self) -> list[tuple[str, str]]:
        if self._memory is not None:
            return list(self._memory)
        if self._sqlite is not None:
            with self._lock:
                rows = self._sqlite.execute(
                    "SELECT visitor_id, page FROM page_views ORDER BY id"
                ).fetchall()
            return [(row[0], row[1]) for row in rows]
        if self._postgres_url is not None:
            import psycopg

            with psycopg.connect(self._postgres_url) as conn, conn.cursor() as cursor:
                cursor.execute("SELECT visitor_id, page FROM page_views ORDER BY id")
                return [(row[0], row[1]) for row in cursor.fetchall()]
        return []

    def _count_today(self) -> int:
        today = date.today().isoformat()
        if self._sqlite is not None:
            with self._lock:
                row = self._sqlite.execute(
                    "SELECT COUNT(*) FROM page_views WHERE substr(created_at, 1, 10) = ?",
                    (today,),
                ).fetchone()
            return int(row[0]) if row else 0
        if self._postgres_url is not None:
            import psycopg

            with psycopg.connect(self._postgres_url) as conn, conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM page_views WHERE created_at::date = %s",
                    (today,),
                )
                row = cursor.fetchone()
            return int(row[0]) if row else 0
        return 0

    def summary(self) -> dict[str, int]:
        views = self._fetch_all()
        return {
            "total_views": len(views),
            "unique_visitors": len({visitor for visitor, _ in views}),
            "visits_today": self._count_today(),
        }
