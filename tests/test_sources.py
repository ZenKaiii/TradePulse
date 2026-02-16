from tradepulse.sources import fetch_articles_from_feeds, get_feeds


def test_get_feeds_for_trader_profile():
    feeds = get_feeds("trader")

    assert len(feeds) > 0
    assert all("name" in feed and "url" in feed for feed in feeds)


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
