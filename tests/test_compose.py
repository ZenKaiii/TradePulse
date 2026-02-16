from tradepulse.compose import compose_digest


def test_compose_contains_direction_ticker_and_sources():
    digest = compose_digest(
        top_events=[
            {
                "title": "NVIDIA raises guidance",
                "summary_zh": "英伟达上调指引，AI需求仍强",
                "direction": "bullish",
                "affected_tickers": [{"symbol": "NVDA", "name": "NVIDIA"}],
                "impact_reason_zh": "AI需求超预期",
                "analysis_level": "detailed",
                "search_context": "外部检索显示多家媒体提到云厂商持续增加GPU采购。",
                "beginner_note_zh": "可理解为企业盈利预期提升",
                "sources": [{"name": "Reuters", "url": "https://reuters.com/x"}],
            }
        ],
        overlays={
            "stocks": [
                {
                    "topic": "NVDA",
                    "count": 1,
                    "items": [
                        {
                            "title": "NVIDIA raises guidance",
                            "source_name": "Reuters",
                            "url": "https://reuters.com/x",
                        }
                    ],
                }
            ],
            "keywords": [],
            "geopolitics": [],
        },
        analysis_meta={"provider": "bailian", "model": "qwen-plus"},
        market_regime={
            "us": {
                "status": "ok",
                "leaders": [{"symbol": "XLK", "name": "Technology", "score": 5.2, "rs_4w": 1.2, "rs_12w": 2.5}],
                "laggards": [{"symbol": "XLU", "name": "Utilities", "score": -2.1, "rs_4w": -0.9, "rs_12w": -1.7}],
                "flow_proxy": {
                    "inflow": [{"symbol": "XLK", "name": "Technology", "flow_proxy": 120000000.0, "change_pct": 1.5, "dollar_volume": 8000000000.0}],
                    "outflow": [{"symbol": "XLU", "name": "Utilities", "flow_proxy": -90000000.0, "change_pct": -1.2, "dollar_volume": 7000000000.0}],
                },
                "stock_flow": {
                    "inflow": [{"symbol": "NVDA", "name": "NVIDIA", "flow_proxy": 210000000.0, "change_pct": 2.8, "dollar_volume": 12000000000.0, "activity_ratio": 1.7}],
                },
            },
            "a_share": {
                "status": "ok",
                "inflow": [{"name": "电子", "net_flow": 1500000000.0}],
                "outflow": [{"name": "地产", "net_flow": -1200000000.0}],
            },
            "sec": {
                "status": "ok",
                "institutions_13f": [{"institution": "BERKSHIRE HATHAWAY INC", "form": "13F-HR", "filing_date": "2025-11-14", "url": "https://sec.example/13f"}],
                "insiders_form4": [{"symbol": "NVDA", "issuer": "NVIDIA CORP", "form": "4", "filing_date": "2026-02-03", "url": "https://sec.example/form4"}],
            },
        },
    )

    assert "利好" in digest
    assert "英伟达上调指引" in digest
    assert "NVDA (NVIDIA)" in digest
    assert "Reuters" in digest
    assert "板块轮动与资金流" in digest
    assert "XLK" in digest
    assert "电子" in digest
    assert "🤖" in digest
    assert "候选观察清单" in digest
    assert "外部检索补充" in digest
    assert "板块当日资金流代理" in digest
    assert "个股资金流入代理" in digest
    assert "机构13F与内部人Form4" in digest


def test_compose_shows_no_new_message_when_top_events_empty():
    digest = compose_digest(
        top_events=[],
        overlays={"stocks": [], "keywords": [], "geopolitics": []},
        analysis_meta={"provider": "rule", "model": "rule-engine"},
        market_regime={},
    )
    assert "本小时无新增关键事件" in digest


def test_compose_defaults_top5_detailed_without_analysis_level():
    top_events = []
    for idx in range(6):
        top_events.append(
            {
                "title": f"event-{idx}",
                "summary_zh": "摘要",
                "direction": "neutral",
                "affected_tickers": [],
                "impact_reason_zh": "原因",
                "sources": [{"name": "src", "url": "https://example.com"}],
            }
        )

    digest = compose_digest(
        top_events=top_events,
        overlays={"stocks": [], "keywords": [], "geopolitics": []},
        analysis_meta={"provider": "rule", "model": "rule-engine"},
        market_regime={},
    )

    assert "1. 📰 event-0（详细）" in digest
    assert "5. 📰 event-4（详细）" in digest
    assert "6. 📰 event-5（简版）" in digest
