from dataclasses import dataclass


@dataclass
class CanonicalArticle:
    id: str
    title: str
    url: str
    source_name: str
    published_at: str
    summary_raw: str = ""
    language: str = "unknown"
