import hashlib
import re


def normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def hash_question(question: str, language: str, state: str, category: str) -> str:
    value = "|".join(
        [
            normalize_question(question),
            language.strip().lower(),
            state.strip().lower(),
            category.strip().lower(),
        ]
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

