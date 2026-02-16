import hashlib
from typing import Dict, List

from tradepulse.models import CanonicalArticle


def parse_rss_entries(source_name: str, entries: List[Dict]) -> List[CanonicalArticle]:
    items: List[CanonicalArticle] = []

    for entry in entries:
        title = str(entry.get("title", "")).strip()
        url = str(entry.get("link", "")).strip()
        published_at = str(entry.get("published", "")).strip()
        summary_raw = str(entry.get("summary", "")).strip()

        raw_id = f"{source_name}|{title}|{url}"
        article_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()

        items.append(
            CanonicalArticle(
                id=article_id,
                title=title,
                url=url,
                source_name=source_name,
                published_at=published_at,
                summary_raw=summary_raw,
            )
        )

    return items
