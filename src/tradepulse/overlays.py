import re
from typing import Any, Dict, List


def match_overlays(
    events: List[Dict[str, Any]],
    stocks: List[str],
    keywords: List[str],
    geopolitics: List[str],
    max_items_per_topic: int = 3,
) -> Dict[str, List[Dict[str, Any]]]:
    normalized_events: List[Dict[str, Any]] = []
    for item in events:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        normalized_events.append(
            {
                "title": title,
                "title_lower": title.lower(),
                "source_name": str(item.get("primary_source") or item.get("source_name") or "Unknown"),
                "url": str(
                    item.get("url")
                    or (item.get("sources") or [{}])[0].get("url", "")
                ),
            }
        )

    stock_hits: List[Dict[str, Any]] = []
    for symbol in stocks:
        token = str(symbol).strip().upper()
        if not token:
            continue
        pattern = re.compile(rf"(?<![A-Za-z0-9])\$?{re.escape(token)}(?![A-Za-z0-9])", re.IGNORECASE)
        matched_items = [
            {
                "title": event["title"],
                "source_name": event["source_name"],
                "url": event["url"],
            }
            for event in normalized_events
            if pattern.search(event["title"])
        ][:max_items_per_topic]
        if matched_items:
            stock_hits.append(
                {
                    "topic": token,
                    "count": len(matched_items),
                    "items": matched_items,
                }
            )

    keyword_hits: List[Dict[str, Any]] = []
    for keyword in keywords:
        phrase = str(keyword).strip()
        if not phrase:
            continue
        needle = phrase.lower()
        matched_items = [
            {
                "title": event["title"],
                "source_name": event["source_name"],
                "url": event["url"],
            }
            for event in normalized_events
            if needle in event["title_lower"]
        ][:max_items_per_topic]
        if matched_items:
            keyword_hits.append(
                {
                    "topic": phrase,
                    "count": len(matched_items),
                    "items": matched_items,
                }
            )

    geo_hits: List[Dict[str, Any]] = []
    for topic in geopolitics:
        normalized_topic = str(topic).strip()
        tokens = [t for t in re.split(r"[-_\s]+", normalized_topic.lower()) if t]
        if not tokens:
            continue
        min_match = 1 if len(tokens) <= 1 else min(2, len(tokens))
        long_tokens = [token for token in tokens if len(token) >= 4]
        matched_items = []
        for event in normalized_events:
            hit_count = sum(1 for token in tokens if re.search(rf"\b{re.escape(token)}\b", event["title_lower"]))
            long_hit_count = sum(
                1 for token in long_tokens if re.search(rf"\b{re.escape(token)}\b", event["title_lower"])
            )
            min_long_match = min(2, len(long_tokens)) if long_tokens else 0
            if hit_count >= min_match and long_hit_count >= min_long_match:
                matched_items.append(
                    {
                        "title": event["title"],
                        "source_name": event["source_name"],
                        "url": event["url"],
                    }
                )
            if len(matched_items) >= max_items_per_topic:
                break
        if matched_items:
            geo_hits.append(
                {
                    "topic": normalized_topic,
                    "count": len(matched_items),
                    "items": matched_items,
                }
            )

    return {"stocks": stock_hits, "keywords": keyword_hits, "geopolitics": geo_hits}
