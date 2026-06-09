import re
from collections import Counter

from ai_agent_service.tools.base import ToolDefinition


def count_words(text: str) -> dict[str, int]:
    words = re.findall(r"[\w']+", text.lower())
    return {
        "characters": len(text),
        "words": len(words),
        "unique_words": len(set(words)),
    }


def slugify(text: str, separator: str = "-") -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", separator, text.lower()).strip(separator)
    return re.sub(rf"{re.escape(separator)}+", separator, normalized)


def extract_keywords(text: str, limit: int = 5) -> list[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
        "it", "of", "on", "or", "that", "the", "to", "with", "this", "was", "were",
    }
    words = [word for word in re.findall(r"[a-zA-Z][a-zA-Z0-9']*", text.lower()) if word not in stopwords]
    return [word for word, _ in Counter(words).most_common(limit)]


def build_text_tools() -> list[ToolDefinition]:
    return [
        ToolDefinition(
            name="count_words",
            description="Count characters, words, and unique words in a text input.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=count_words,
        ),
        ToolDefinition(
            name="slugify",
            description="Convert a title or label into a URL-friendly slug.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "separator": {"type": "string", "default": "-"},
                },
                "required": ["text"],
            },
            handler=slugify,
        ),
        ToolDefinition(
            name="extract_keywords",
            description="Extract the most common non-stopword keywords from English text.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                },
                "required": ["text"],
            },
            handler=extract_keywords,
        ),
    ]
