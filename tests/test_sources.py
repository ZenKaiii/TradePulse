from tradepulse.sources import (
    evaluate_feed_health,
    fetch_articles_from_feeds,
    fetch_articles_with_health,
    get_feeds,
)


def test_get_feeds_for_trader_profile():
    feeds = get_feeds("trader", tier="core")

    assert len(feeds) > 0
    assert all("name" in feed and "url" in feed for feed in feeds)
    assert all(feed.get("tier") == "core" for feed in feeds)


def test_get_feeds_for_extended_includes_core_and_extended():
    core_feeds = get_feeds("trader", tier="core")
    extended_feeds = get_feeds("trader", tier="extended")

    assert len(extended_feeds) >= len(core_feeds)
    assert any(feed.get("tier") == "extended" for feed in extended_feeds)


def test_fetch_articles_from_feeds_with_parser_stub():
    class FeedResult:
        def __init__(self):
            self.entries = [
                {
                    "title": "Fed minutes signal caution",
                    "link": "https://example.com/fed-minutes",
                    "published": "Mon, 01 Jan 2026 00:00:00 GMT",
                    "summary": "Summary",
                }
            ]

    def parser_stub(_url):
        return FeedResult()

    items = fetch_articles_from_feeds("trader", parser=parser_stub, max_per_feed=1)
    assert items
    assert items[0].title == "Fed minutes signal caution"


def test_fetch_articles_with_health_returns_health_records():
    class FeedResult:
        def __init__(self):
            self.entries = [
                {
                    "title": "Fed minutes signal caution",
                    "link": "https://example.com/fed-minutes",
                    "published": "Mon, 01 Jan 2026 00:00:00 GMT",
                    "summary": "Summary",
                }
            ]

    def parser_stub(_url):
        return FeedResult()

    items, health = fetch_articles_with_health(
        "trader", tier="core", parser=parser_stub, max_per_feed=1
    )
    assert items
    assert health
    assert all(h.ok for h in health)
    assert all(h.health_score > 0 for h in health)


def test_evaluate_feed_health_penalizes_empty_or_error():
    good = evaluate_feed_health(ok=True, entry_count=20, error="")
    empty = evaluate_feed_health(ok=True, entry_count=0, error="")
    bad = evaluate_feed_health(ok=False, entry_count=0, error="timeout")

    assert good > empty
    assert empty > bad
