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
        market_regime={
            "us": {
                "status": "ok",
                "leaders": [{"symbol": "XLK", "name": "Technology", "score": 5.2}],
                "laggards": [{"symbol": "XLU", "name": "Utilities", "score": -2.1}],
            },
            "a_share": {
                "status": "ok",
                "inflow": [{"name": "电子", "net_flow": 1500000000.0}],
                "outflow": [{"name": "地产", "net_flow": -1200000000.0}],
            },
        },
    )

    assert "利好" in digest
    assert "NVDA (NVIDIA)" in digest
    assert "Reuters" in digest
    assert "板块轮动与资金流" in digest
    assert "XLK" in digest
    assert "电子" in digest
