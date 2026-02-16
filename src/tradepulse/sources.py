from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import feedparser

from tradepulse.ingest import parse_rss_entries
from tradepulse.models import CanonicalArticle

Feed = Dict[str, str]


FEED_PROFILES: Dict[str, List[Feed]] = {
    "trader": [
        {
            "name": "Federal Reserve",
            "url": "https://www.federalreserve.gov/feeds/press_all.xml",
            "tier": "core",
        },
        {"name": "SEC Press", "url": "https://www.sec.gov/news/pressreleases.rss", "tier": "core"},
        {
            "name": "MarketWatch",
            "url": "https://feeds.marketwatch.com/marketwatch/topstories",
            "tier": "core",
        },
        {"name": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html", "tier": "core"},
        {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "tier": "core"},
        {
            "name": "Google News Business",
            "url": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
            "tier": "extended",
        },
        {
            "name": "Google News US Market",
            "url": "https://news.google.com/rss/search?q=US+stock+market+when:1d&hl=en-US&gl=US&ceid=US:en",
            "tier": "extended",
        },
        {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml", "tier": "extended"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "tier": "extended"},
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "tier": "experimental"},
    ],
    "balanced": [
        {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "tier": "core"},
        {"name": "Reuters World", "url": "https://feeds.reuters.com/Reuters/worldNews", "tier": "core"},
        {
            "name": "MarketWatch",
            "url": "https://feeds.marketwatch.com/marketwatch/topstories",
            "tier": "core",
        },
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "tier": "extended"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "tier": "extended"},
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "tier": "experimental"},
    ],
}


TIER_ORDER = {"core": 0, "extended": 1, "experimental": 2}


@dataclass
class FeedHealth:
    name: str
    url: str
    tier: str
    ok: bool
    entry_count: int
    health_score: int
    error: str = ""


def evaluate_feed_health(ok: bool, entry_count: int, error: str) -> int:
    score = 50
    score += 20 if ok else -40
    score += min(max(entry_count, 0), 30)
    if entry_count <= 0:
        score -= 25
    if error:
        score -= 20
    return max(0, min(100, score))


def get_feeds(profile: str, tier: str = "core") -> List[Feed]:
    all_feeds = FEED_PROFILES.get(profile, FEED_PROFILES["trader"])
    max_tier = TIER_ORDER.get(tier, TIER_ORDER["core"])
    selected = []
    for feed in all_feeds:
        feed_tier = feed.get("tier", "core")
        if TIER_ORDER.get(feed_tier, 99) <= max_tier:
            selected.append(feed)
    return selected


def fetch_articles_from_feeds(
    profile: str,
    tier: str = "core",
    parser: Callable = feedparser.parse,
    max_per_feed: int = 20,
) -> List[CanonicalArticle]:
    items, _ = fetch_articles_with_health(profile=profile, tier=tier, parser=parser, max_per_feed=max_per_feed)
    return items


def fetch_articles_with_health(
    profile: str,
    tier: str = "core",
    parser: Callable = feedparser.parse,
    max_per_feed: int = 20,
) -> Tuple[List[CanonicalArticle], List[FeedHealth]]:
    all_items: List[CanonicalArticle] = []
    health_records: List[FeedHealth] = []
    for feed in get_feeds(profile, tier=tier):
        feed_name = feed["name"]
        feed_url = feed["url"]
        feed_tier = feed.get("tier", "core")
        error = ""
        try:
            parsed = parser(feed_url)
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
            all_items.extend(parse_rss_entries(feed_name, entries))
            health_records.append(
                FeedHealth(
                    name=feed_name,
                    url=feed_url,
                    tier=feed_tier,
                    ok=True,
                    entry_count=len(entries),
                    health_score=evaluate_feed_health(ok=True, entry_count=len(entries), error=""),
                )
            )
        except Exception as exc:
            error = str(exc)
            health_records.append(
                FeedHealth(
                    name=feed_name,
                    url=feed_url,
                    tier=feed_tier,
                    ok=False,
                    entry_count=0,
                    health_score=evaluate_feed_health(ok=False, entry_count=0, error=error),
                    error=error,
                )
            )
            continue
    return all_items, health_records
