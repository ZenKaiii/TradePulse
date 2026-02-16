import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from io import StringIO
from typing import Any, Callable, Dict, List

import httpx

US_BENCHMARK_SYMBOLS = ("SPY", "QQQ")
US_SECTOR_NAMES = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLI": "Industrials",
    "XLC": "Communication Services",
    "XLRE": "Real Estate",
    "XLB": "Materials",
    "XLU": "Utilities",
}
A_SHARE_FLOW_URL = (
    "https://push2.eastmoney.com/api/qt/clist/get"
    "?pn=1&pz=200&po={order}&np=1&ut=b2884a393a59ad64002292a3e90d46a5"
    "&fltt=2&invt=2&fid=f62&fs=m:90+t:2"
    "&fields=f12,f14,f2,f3,f62,f184"
)


@dataclass
class MarketRegimeOptions:
    enabled: bool = True
    us_enabled: bool = True
    a_share_enabled: bool = True
    us_top_n: int = 3
    a_share_top_n: int = 5
    request_timeout_sec: float = 8.0


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _pct_return(prices: List[float], sessions: int) -> float:
    if len(prices) < 2:
        return 0.0
    start_index = max(0, len(prices) - 1 - sessions)
    start = prices[start_index]
    end = prices[-1]
    if start <= 0:
        return 0.0
    return (end / start) - 1.0


def fetch_us_prices(symbol: str, timeout_sec: float) -> List[float]:
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d"
    response = httpx.get(url, timeout=timeout_sec)
    response.raise_for_status()

    rows = csv.DictReader(StringIO(response.text))
    prices: List[float] = []
    for row in rows:
        close_price = _to_float(row.get("Close"))
        if close_price > 0:
            prices.append(close_price)

    if len(prices) < 2:
        raise ValueError(f"no valid prices for {symbol}")
    return prices


def compute_us_sector_rankings(price_map: Dict[str, List[float]], top_n: int = 3) -> Dict[str, Any]:
    spy_prices = price_map.get("SPY")
    qqq_prices = price_map.get("QQQ")
    if not spy_prices or not qqq_prices:
        raise ValueError("benchmarks SPY and QQQ are required")

    spy_4w = _pct_return(spy_prices, 20)
    spy_12w = _pct_return(spy_prices, 60)
    qqq_4w = _pct_return(qqq_prices, 20)
    qqq_12w = _pct_return(qqq_prices, 60)

    entries: List[Dict[str, Any]] = []
    for symbol, sector_name in US_SECTOR_NAMES.items():
        prices = price_map.get(symbol)
        if not prices:
            continue

        sector_4w = _pct_return(prices, 20)
        sector_12w = _pct_return(prices, 60)

        rs_4w = ((sector_4w - spy_4w) + (sector_4w - qqq_4w)) / 2.0 * 100.0
        rs_12w = ((sector_12w - spy_12w) + (sector_12w - qqq_12w)) / 2.0 * 100.0
        score = rs_4w * 0.6 + rs_12w * 0.4

        entries.append(
            {
                "symbol": symbol,
                "name": sector_name,
                "rs_4w": round(rs_4w, 2),
                "rs_12w": round(rs_12w, 2),
                "score": round(score, 2),
            }
        )

    if not entries:
        raise ValueError("no sector data available")

    leaders = sorted(entries, key=lambda item: item["score"], reverse=True)[:top_n]
    laggards = sorted(entries, key=lambda item: item["score"])[:top_n]
    return {"leaders": leaders, "laggards": laggards}


def fetch_a_share_flow(timeout_sec: float) -> Dict[str, Any]:
    inflow_response = httpx.get(A_SHARE_FLOW_URL.format(order=1), timeout=timeout_sec)
    inflow_response.raise_for_status()
    inflow_payload = inflow_response.json()

    outflow_response = httpx.get(A_SHARE_FLOW_URL.format(order=0), timeout=timeout_sec)
    outflow_response.raise_for_status()
    outflow_payload = outflow_response.json()

    if not isinstance(inflow_payload, dict) or not isinstance(outflow_payload, dict):
        raise ValueError("invalid eastmoney payload")
    return {"inflow_payload": inflow_payload, "outflow_payload": outflow_payload}


def _extract_a_share_entries(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = payload.get("data", {}).get("diff", [])
    if not isinstance(rows, list):
        rows = []

    entries: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue

        name = str(row.get("f14", "")).strip()
        if not name:
            continue

        entries.append(
            {
                "code": str(row.get("f12", "")),
                "name": name,
                "net_flow": _to_float(row.get("f62")),
                "change_pct": _to_float(row.get("f3")),
            }
        )

    return entries


def parse_a_share_flow(payload: Dict[str, Any], top_n: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    entries = _extract_a_share_entries(payload)

    inflow = sorted(entries, key=lambda item: item["net_flow"], reverse=True)[:top_n]
    outflow = sorted(entries, key=lambda item: item["net_flow"])[:top_n]
    return {"inflow": inflow, "outflow": outflow}


def _fetch_us_price_map(
    symbols: List[str],
    timeout_sec: float,
    price_fetcher: Callable[[str, float], List[float]],
) -> Dict[str, List[float]]:
    if not symbols:
        return {}

    price_map: Dict[str, List[float]] = {}
    with ThreadPoolExecutor(max_workers=min(len(symbols), 6)) as executor:
        future_map = {
            executor.submit(price_fetcher, symbol, timeout_sec): symbol for symbol in symbols
        }
        for future in as_completed(future_map):
            symbol = future_map[future]
            price_map[symbol] = future.result()
    return price_map


def build_market_regime_snapshot(
    options: MarketRegimeOptions,
    us_price_fetcher: Callable[[str, float], List[float]] = fetch_us_prices,
    a_share_fetcher: Callable[[float], Dict[str, Any]] = fetch_a_share_flow,
) -> Dict[str, Any]:
    if not options.enabled:
        return {}

    snapshot: Dict[str, Any] = {}

    if options.us_enabled:
        try:
            symbols = list(US_BENCHMARK_SYMBOLS) + list(US_SECTOR_NAMES.keys())
            price_map = _fetch_us_price_map(
                symbols=symbols,
                timeout_sec=options.request_timeout_sec,
                price_fetcher=us_price_fetcher,
            )
            ranked = compute_us_sector_rankings(price_map, top_n=options.us_top_n)
            snapshot["us"] = {"status": "ok", **ranked}
        except Exception:
            snapshot["us"] = {
                "status": "unavailable",
                "message": "美股板块强弱数据暂不可用",
            }

    if options.a_share_enabled:
        try:
            payload = a_share_fetcher(options.request_timeout_sec)
            if (
                isinstance(payload, dict)
                and "inflow_payload" in payload
                and "outflow_payload" in payload
            ):
                inflow_rows = _extract_a_share_entries(payload["inflow_payload"])
                outflow_rows = _extract_a_share_entries(payload["outflow_payload"])
                ranked_flow = {
                    "inflow": sorted(
                        inflow_rows,
                        key=lambda item: item["net_flow"],
                        reverse=True,
                    )[: options.a_share_top_n],
                    "outflow": sorted(
                        outflow_rows,
                        key=lambda item: item["net_flow"],
                    )[: options.a_share_top_n],
                }
            else:
                ranked_flow = parse_a_share_flow(payload, top_n=options.a_share_top_n)
            if not ranked_flow["inflow"] and not ranked_flow["outflow"]:
                raise ValueError("empty A-share flow rows")
            snapshot["a_share"] = {"status": "ok", **ranked_flow}
        except Exception:
            snapshot["a_share"] = {
                "status": "unavailable",
                "message": "A股资金流数据暂不可用",
            }

    return snapshot
