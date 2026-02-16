from tradepulse.sources import get_feeds


def test_extended_tier_includes_google_news_feeds():
    feeds = get_feeds("trader", tier="extended")
    names = {item["name"] for item in feeds}

    assert "Google News Business" in names
