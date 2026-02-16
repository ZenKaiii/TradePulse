from typing import Callable, Dict, List

import feedparser

from tradepulse.ingest import parse_rss_entries
from tradepulse.models import CanonicalArticle

Feed = Dict[str, str]


FEED_PROFILES: Dict[str, List[Feed]] = {
    "trader": [
        {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
        {"name": "SEC Press", "url": "https://www.sec.gov/news/pressreleases.rss"},
        {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories"},
        {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
        {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex"},
        {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    ],
    "balanced": [
        {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
        {"name": "Reuters World", "url": "https://feeds.reuters.com/Reuters/worldNews"},
        {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    ],
}


def get_feeds(profile: str) -> List[Feed]:
    return FEED_PROFILES.get(profile, FEED_PROFILES["trader"])


def fetch_articles_from_feeds(
    profile: str,
    parser: Callable = feedparser.parse,
    max_per_feed: int = 20,
) -> List[CanonicalArticle]:
    all_items: List[CanonicalArticle] = []
    for feed in get_feeds(profile):
        try:
            parsed = parser(feed["url"])
            entries = []
            for item in list(getattr(parsed, "entries", []))[:max_per_feed]:
                entries.append(
                    {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "published": item.get("published", "") or item.get("updated", ""),
                        "summary": item.get("summary", ""),
                    }
                )
            all_items.extend(parse_rss_entries(feed["name"], entries))
        except Exception:
            continue
    return all_items
