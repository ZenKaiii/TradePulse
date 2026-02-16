import pytest

from tradepulse.market.regime import (
    MarketRegimeOptions,
    build_market_regime_snapshot,
    compute_us_flow_proxy_rankings,
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


def test_compute_us_flow_proxy_rankings_prefers_positive_flow():
    metrics_map = {
        "XLK": {
            "symbol": "XLK",
            "name": "Technology",
            "change_pct": 1.8,
            "dollar_volume": 9_000_000_000.0,
            "flow_proxy": 162_000_000.0,
        },
        "XLE": {
            "symbol": "XLE",
            "name": "Energy",
            "change_pct": -1.1,
            "dollar_volume": 8_000_000_000.0,
            "flow_proxy": -88_000_000.0,
        },
    }

    ranked = compute_us_flow_proxy_rankings(metrics_map, top_n=1)
    assert ranked["inflow"][0]["symbol"] == "XLK"
    assert ranked["outflow"][0]["symbol"] == "XLE"


def test_compute_us_flow_proxy_rankings_filters_wrong_direction_lists():
    ranked_positive_only = compute_us_flow_proxy_rankings(
        {"XLK": {"symbol": "XLK", "flow_proxy": 10.0}},
        top_n=3,
    )
    assert ranked_positive_only["inflow"][0]["symbol"] == "XLK"
    assert ranked_positive_only["outflow"] == []

    ranked_negative_only = compute_us_flow_proxy_rankings(
        {"XLE": {"symbol": "XLE", "flow_proxy": -5.0}},
        top_n=3,
    )
    assert ranked_negative_only["inflow"] == []
    assert ranked_negative_only["outflow"][0]["symbol"] == "XLE"


def test_market_snapshot_includes_us_flow_stock_flow_and_disclosures():
    options = MarketRegimeOptions(
        enabled=True,
        us_enabled=True,
        a_share_enabled=False,
        us_top_n=1,
        us_stock_flow_top_n=1,
        stock_universe=["NVDA"],
        sec_enabled=True,
        sec_13f_ciks=["0001067983"],
    )

    def _fake_us_prices(symbol: str, timeout_sec: float):
        return _linear_prices(100.0, 120.0)

    def _fake_us_flow(symbol: str, timeout_sec: float):
        boost = 3.0 if symbol == "XLK" else (2.0 if symbol == "NVDA" else 1.0)
        return {
            "symbol": symbol,
            "name": symbol,
            "change_pct": boost,
            "dollar_volume": 1_000_000_000.0,
            "flow_proxy": 10_000_000.0 * boost,
            "activity_ratio": 1.4,
        }

    def _fake_sec_disclosures(symbols, ciks, timeout_sec, user_agent):
        return {
            "status": "ok",
            "institutions_13f": [
                {
                    "institution": "BERKSHIRE HATHAWAY INC",
                    "form": "13F-HR",
                    "filing_date": "2025-11-14",
                    "url": "https://sec.example/13f",
                }
            ],
            "insiders_form4": [
                {
                    "symbol": "NVDA",
                    "issuer": "NVIDIA CORP",
                    "form": "4",
                    "filing_date": "2026-02-03",
                    "url": "https://sec.example/form4",
                }
            ],
        }

    snapshot = build_market_regime_snapshot(
        options=options,
        us_price_fetcher=_fake_us_prices,
        us_flow_fetcher=_fake_us_flow,
        sec_disclosure_fetcher=_fake_sec_disclosures,
    )

    assert snapshot["us"]["status"] == "ok"
    assert snapshot["us"]["flow_proxy"]["inflow"][0]["symbol"] == "XLK"
    assert snapshot["us"]["stock_flow"]["inflow"][0]["symbol"] == "NVDA"
    assert snapshot["sec"]["status"] == "ok"
    assert snapshot["sec"]["institutions_13f"][0]["form"] == "13F-HR"
