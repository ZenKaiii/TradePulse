from tradepulse.compose import compose_digest


def test_compose_contains_direction_ticker_and_sources():
    digest = compose_digest(
        top_events=[
            {
                "title": "NVIDIA raises guidance",
                "direction": "bullish",
                "affected_tickers": [{"symbol": "NVDA", "name": "NVIDIA"}],
                "impact_reason_zh": "AI需求超预期",
                "sources": [{"name": "Reuters", "url": "https://reuters.com/x"}],
            }
        ],
        overlays={},
    )

    assert "利好" in digest
    assert "NVDA (NVIDIA)" in digest
    assert "Reuters" in digest
