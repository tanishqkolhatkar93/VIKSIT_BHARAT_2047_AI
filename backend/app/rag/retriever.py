import json
from pathlib import Path

from app.schemas import Source


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge_documents.json"


def tokenize(text: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in text.split()
        if len(token.strip(".,:;!?()[]{}\"'")) > 2
    }


class KnowledgeRetriever:
    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.documents = json.loads(data_path.read_text(encoding="utf-8"))

    def search(self, question: str, category: str, state: str, limit: int = 6) -> list[dict]:
        query = tokenize(question)
        scored: list[tuple[int, dict]] = []
        for document in self.documents:
            haystack = " ".join(
                [
                    document["title"],
                    document["source"],
                    document["content"],
                ]
            )
            overlap = query & tokenize(haystack)
            score = len(overlap) * 10
            if document["category"].lower() == category.lower():
                score += 5
            if document["state"] in {state, "All India"}:
                score += 2
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        selected: list[dict] = []
        per_title: dict[str, int] = {}
        for _, document in scored:
            base = document["title"].split(" (Part")[0]
            if per_title.get(base, 0) >= 2:
                continue
            selected.append(document)
            per_title[base] = per_title.get(base, 0) + 1
            if len(selected) >= limit:
                break
        return selected

    @staticmethod
    def sources(documents: list[dict]) -> list[Source]:
        return [
            Source(
                title=document["title"],
                source=document["source"],
                url=document["url"],
                category=document["category"],
                state=document["state"],
                date=document["date"],
            )
            for document in documents
        ]
