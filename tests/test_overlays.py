from tradepulse.overlays import match_overlays


def test_keyword_overlay_hits_without_filtering_mainline():
    overlays = match_overlays(
        [
            {
                "title": "US announces new export controls on AI chips",
                "source_name": "Reuters",
                "url": "https://example.com/export-controls",
            }
        ],
        stocks=["NVDA"],
        keywords=["export controls"],
        geopolitics=["us-china-tech"],
    )

    assert overlays["keywords"][0]["topic"] == "export controls"
    assert overlays["keywords"][0]["count"] == 1


def test_stock_overlay_uses_word_boundary_for_short_tickers():
    overlays = match_overlays(
        [
            {
                "title": "Local community banks face tighter funding conditions",
                "source_name": "MarketWatch",
                "url": "https://example.com/community",
            },
            {
                "title": "MU beats quarterly estimates on memory-chip demand",
                "source_name": "CNBC",
                "url": "https://example.com/mu-beats",
            },
        ],
        stocks=["MU"],
        keywords=[],
        geopolitics=[],
    )

    assert overlays["stocks"][0]["topic"] == "MU"
    assert overlays["stocks"][0]["count"] == 1
    assert overlays["stocks"][0]["items"][0]["title"].startswith("MU beats")


def test_geopolitics_overlay_requires_multi_token_context():
    overlays = match_overlays(
        [
            {
                "title": "US tech exports to China face new licensing rules",
                "source_name": "Bloomberg",
                "url": "https://example.com/us-china-tech",
            },
            {
                "title": "US tech stocks rally into close",
                "source_name": "Yahoo Finance",
                "url": "https://example.com/us-tech-rally",
            },
        ],
        stocks=[],
        keywords=[],
        geopolitics=["us-china-tech"],
    )

    assert overlays["geopolitics"][0]["topic"] == "us-china-tech"
    assert overlays["geopolitics"][0]["count"] == 1
