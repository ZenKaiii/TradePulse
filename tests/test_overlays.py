from tradepulse.overlays import match_overlays


def test_keyword_overlay_hits_without_filtering_mainline():
    overlays = match_overlays(
        ["US announces new export controls on AI chips"],
        stocks=["NVDA"],
        keywords=["export controls"],
        geopolitics=["us-china-tech"],
    )

    assert overlays["keywords"]
