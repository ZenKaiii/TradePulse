import pytest

from tradepulse.market.regime import (
    MarketRegimeOptions,
    build_market_regime_snapshot,
    compute_us_sector_rankings,
    parse_a_share_flow,
)


def _linear_prices(start: float, end: float, points: int = 70):
    step = (end - start) / float(points - 1)
    return [start + step * index for index in range(points)]


def test_compute_us_sector_rankings_prefers_stronger_sectors():
    price_map = {
        "SPY": _linear_prices(100.0, 110.0),
        "QQQ": _linear_prices(100.0, 115.0),
        "XLK": _linear_prices(100.0, 130.0),
        "XLF": _linear_prices(100.0, 118.0),
        "XLE": _linear_prices(100.0, 95.0),
    }

    ranked = compute_us_sector_rankings(price_map, top_n=2)

    assert ranked["leaders"][0]["symbol"] == "XLK"
    assert ranked["laggards"][0]["symbol"] == "XLE"


def test_parse_a_share_flow_returns_inflow_and_outflow():
    payload = {
        "data": {
            "diff": [
                {"f14": "电子", "f62": 1500000000.0, "f3": 0.8, "f12": "BK1201"},
                {"f14": "银行", "f62": -500000000.0, "f3": -0.3, "f12": "BK0475"},
                {"f14": "半导体", "f62": 800000000.0, "f3": 1.6, "f12": "BK1036"},
                {"f14": "地产", "f62": -1200000000.0, "f3": -1.1, "f12": "BK0474"},
            ]
        }
    }

    parsed = parse_a_share_flow(payload, top_n=2)

    assert parsed["inflow"][0]["name"] == "电子"
    assert parsed["outflow"][0]["name"] == "地产"


def test_market_snapshot_degrades_when_us_provider_fails():
    options = MarketRegimeOptions(enabled=True, us_enabled=True, a_share_enabled=True)

    def _broken_us(symbol: str, timeout_sec: float):
        raise RuntimeError("network error")

    def _fake_a_share(timeout_sec: float):
        return {"data": {"diff": [{"f14": "电子", "f62": 600000000.0, "f3": 1.2, "f12": "BK1201"}]}}

    snapshot = build_market_regime_snapshot(
        options=options,
        us_price_fetcher=_broken_us,
        a_share_fetcher=_fake_a_share,
    )

    assert snapshot["us"]["status"] == "unavailable"
    assert snapshot["a_share"]["status"] == "ok"


def test_market_snapshot_uses_separate_a_share_inflow_and_outflow_payloads():
    options = MarketRegimeOptions(enabled=True, us_enabled=False, a_share_enabled=True, a_share_top_n=2)

    def _fake_a_share_pair(timeout_sec: float):
        return {
            "inflow_payload": {
                "data": {
                    "diff": [
                        {"f14": "电子", "f62": 1200000000.0, "f3": 0.8, "f12": "BK1201"},
                        {"f14": "半导体", "f62": 900000000.0, "f3": 1.1, "f12": "BK1036"},
                    ]
                }
            },
            "outflow_payload": {
                "data": {
                    "diff": [
                        {"f14": "地产", "f62": -1300000000.0, "f3": -1.2, "f12": "BK0474"},
                        {"f14": "银行", "f62": -600000000.0, "f3": -0.3, "f12": "BK0475"},
                    ]
                }
            },
        }

    snapshot = build_market_regime_snapshot(
        options=options,
        a_share_fetcher=_fake_a_share_pair,
    )

    assert snapshot["a_share"]["status"] == "ok"
    assert snapshot["a_share"]["inflow"][0]["name"] == "电子"
    assert snapshot["a_share"]["outflow"][0]["name"] == "地产"


def test_market_snapshot_returns_empty_when_disabled():
    snapshot = build_market_regime_snapshot(options=MarketRegimeOptions(enabled=False))
    assert snapshot == {}
