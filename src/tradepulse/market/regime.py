import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from io import StringIO
from typing import Any, Callable, Dict, List, Mapping

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
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
NASDAQ_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
DEFAULT_SEC_13F_CIKS = [
    "0001067983",  # Berkshire Hathaway
    "0001350694",  # Bridgewater Associates
    "0001037389",  # Renaissance Technologies
    "0001649339",  # Scion Asset Management
    "0001167483",  # Tiger Global
    "0001423053",  # Citadel Advisors
]


@dataclass
class MarketRegimeOptions:
    enabled: bool = True
    us_enabled: bool = True
    a_share_enabled: bool = True
    us_top_n: int = 3
    us_stock_flow_top_n: int = 5
    us_market_flow_enabled: bool = True
    us_market_flow_top_n: int = 20
    us_market_flow_universe_size: int = 300
    a_share_top_n: int = 5
    request_timeout_sec: float = 8.0
    stock_universe: List[str] = field(default_factory=list)
    sec_enabled: bool = False
    sec_13f_ciks: List[str] = field(default_factory=lambda: list(DEFAULT_SEC_13F_CIKS))
    sec_user_agent: str = "TradePulse/0.1 (contact: tradepulse@example.com)"


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
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


def _parse_stooq_rows(symbol: str, timeout_sec: float) -> List[Dict[str, Any]]:
    url = f"https://stooq.com/q/d/l/?s={symbol.lower()}.us&i=d"
    response = httpx.get(url, timeout=timeout_sec)
    response.raise_for_status()

    rows: List[Dict[str, Any]] = []
    for row in csv.DictReader(StringIO(response.text)):
        close_price = _to_float(row.get("Close"))
        volume = _to_int(row.get("Volume"))
        if close_price <= 0:
            continue
        rows.append(
            {
                "date": str(row.get("Date", "")),
                "close": close_price,
                "volume": max(volume, 0),
            }
        )
    return rows


def fetch_us_prices(symbol: str, timeout_sec: float) -> List[float]:
    rows = _parse_stooq_rows(symbol, timeout_sec)
    prices = [float(row["close"]) for row in rows if float(row["close"]) > 0]
    if len(prices) < 2:
        raise ValueError(f"no valid prices for {symbol}")
    return prices


def fetch_us_flow_metrics(symbol: str, timeout_sec: float) -> Dict[str, Any]:
    rows = _parse_stooq_rows(symbol, timeout_sec)
    if len(rows) < 2:
        raise ValueError(f"insufficient OHLCV rows for {symbol}")

    last = rows[-1]
    prev = rows[-2]
    last_close = float(last["close"])
    prev_close = float(prev["close"])
    change_pct = ((last_close / prev_close) - 1.0) * 100.0 if prev_close > 0 else 0.0

    dollar_volume = last_close * float(last["volume"])
    recent = rows[-20:] if len(rows) >= 20 else rows
    avg_dollar_volume = sum(float(item["close"]) * float(item["volume"]) for item in recent) / max(len(recent), 1)
    activity_ratio = (dollar_volume / avg_dollar_volume) if avg_dollar_volume > 0 else 0.0
    flow_proxy = dollar_volume * (change_pct / 100.0)

    return {
        "symbol": symbol.upper(),
        "name": US_SECTOR_NAMES.get(symbol.upper(), symbol.upper()),
        "change_pct": round(change_pct, 2),
        "dollar_volume": round(dollar_volume, 2),
        "flow_proxy": round(flow_proxy, 2),
        "activity_ratio": round(activity_ratio, 2),
    }


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


def compute_us_flow_proxy_rankings(metrics_map: Dict[str, Dict[str, Any]], top_n: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    entries = [item for item in metrics_map.values() if isinstance(item, dict)]
    if not entries:
        return {"inflow": [], "outflow": []}
    inflow_candidates = [item for item in entries if float(item.get("flow_proxy", 0.0)) > 0]
    outflow_candidates = [item for item in entries if float(item.get("flow_proxy", 0.0)) < 0]
    inflow = sorted(
        inflow_candidates,
        key=lambda item: float(item.get("flow_proxy", 0.0)),
        reverse=True,
    )[:top_n]
    outflow = sorted(
        outflow_candidates,
        key=lambda item: float(item.get("flow_proxy", 0.0)),
    )[:top_n]
    return {"inflow": inflow, "outflow": outflow}


def _fetch_us_price_map(
    symbols: List[str],
    timeout_sec: float,
    price_fetcher: Callable[[str, float], List[float]],
) -> Dict[str, List[float]]:
    if not symbols:
        return {}

    price_map: Dict[str, List[float]] = {}
    with ThreadPoolExecutor(max_workers=min(len(symbols), 8)) as executor:
        future_map = {
            executor.submit(price_fetcher, symbol, timeout_sec): symbol for symbol in symbols
        }
        for future in as_completed(future_map):
            symbol = future_map[future]
            try:
                price_map[symbol] = future.result()
            except Exception as exc:
                print(f"[tradepulse][market] price fetch failed for {symbol}: {str(exc)}")
    return price_map


def _fetch_us_flow_map(
    symbols: List[str],
    timeout_sec: float,
    flow_fetcher: Callable[[str, float], Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    if not symbols:
        return {}

    flow_map: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(len(symbols), 8)) as executor:
        future_map = {
            executor.submit(flow_fetcher, symbol, timeout_sec): symbol for symbol in symbols
        }
        for future in as_completed(future_map):
            symbol = future_map[future]
            try:
                flow_map[symbol] = future.result()
            except Exception as exc:
                print(f"[tradepulse][market] flow fetch failed for {symbol}: {str(exc)}")
    return flow_map


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


def fetch_nasdaq_symbols(timeout_sec: float) -> List[str]:
    symbols = []
    
    try:
        response = httpx.get(NASDAQ_LISTED_URL, timeout=timeout_sec)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        for line in lines[1:]:
            parts = line.split('|')
            if len(parts) >= 2:
                symbol = parts[0].strip()
                if symbol and symbol.isalpha():
                    symbols.append(symbol)
    except Exception as exc:
        print(f"[tradepulse][market] NASDAQ listed fetch failed: {exc}")
    
    try:
        response = httpx.get(OTHER_LISTED_URL, timeout=timeout_sec)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        for line in lines[1:]:
            parts = line.split('|')
            if len(parts) >= 2:
                symbol = parts[0].strip()
                if symbol and symbol.isalpha():
                    symbols.append(symbol)
    except Exception as exc:
        print(f"[tradepulse][market] Other listed fetch failed: {exc}")
    
    return list(set(symbols))[:500]


def _normalize_cik(value: str) -> str:
    digits = "".join(char for char in str(value or "") if char.isdigit())
    return digits.zfill(10) if digits else ""


def fetch_sec_company_tickers(timeout_sec: float, user_agent: str) -> Dict[str, Dict[str, str]]:
    response = httpx.get(
        SEC_COMPANY_TICKERS_URL,
        timeout=timeout_sec,
        headers={"User-Agent": user_agent},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        return {}

    mapping: Dict[str, Dict[str, str]] = {}
    for item in payload.values():
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("ticker", "")).upper().strip()
        if not symbol:
            continue
        mapping[symbol] = {
            "symbol": symbol,
            "name": str(item.get("title", symbol)).strip(),
            "cik": _normalize_cik(str(item.get("cik_str", ""))),
        }
    return mapping


def fetch_sec_submissions(cik: str, timeout_sec: float, user_agent: str) -> Dict[str, Any]:
    response = httpx.get(
        f"https://data.sec.gov/submissions/CIK{_normalize_cik(cik)}.json",
        timeout=timeout_sec,
        headers={"User-Agent": user_agent},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("invalid SEC submissions payload")
    return payload


def _build_sec_filing_url(cik: str, accession_number: str) -> str:
    normalized_cik = str(int(_normalize_cik(cik)))
    normalized_accession = accession_number.replace("-", "")
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{normalized_cik}/{normalized_accession}/{accession_number}-index.html"
    )


def build_sec_disclosure_snapshot(
    stock_symbols: List[str],
    institution_ciks: List[str],
    timeout_sec: float,
    user_agent: str,
    ticker_map_fetcher: Callable[[float, str], Dict[str, Dict[str, str]]] = fetch_sec_company_tickers,
    submission_fetcher: Callable[[str, float, str], Dict[str, Any]] = fetch_sec_submissions,
) -> Dict[str, Any]:
    institutions_13f: List[Dict[str, str]] = []
    insiders_form4: List[Dict[str, str]] = []

    for cik in [value for value in institution_ciks if _normalize_cik(value)]:
        try:
            submission = submission_fetcher(cik, timeout_sec, user_agent)
            name = str(submission.get("name", cik)).strip()
            recent = submission.get("filings", {}).get("recent", {})
            forms = recent.get("form", []) or []
            dates = recent.get("filingDate", []) or []
            accession_numbers = recent.get("accessionNumber", []) or []
            for form, filing_date, accession_number in zip(forms, dates, accession_numbers):
                if not str(form).startswith("13F"):
                    continue
                institutions_13f.append(
                    {
                        "institution": name,
                        "cik": _normalize_cik(cik),
                        "form": str(form),
                        "filing_date": str(filing_date),
                        "url": _build_sec_filing_url(cik, str(accession_number)),
                    }
                )
                break
        except Exception as exc:
            print(f"[tradepulse][sec] 13F fetch failed for CIK={cik}: {str(exc)}")

    ticker_map: Dict[str, Dict[str, str]] = {}
    if stock_symbols:
        try:
            ticker_map = ticker_map_fetcher(timeout_sec, user_agent)
        except Exception as exc:
            print(f"[tradepulse][sec] ticker map fetch failed: {str(exc)}")

    for symbol in sorted({value.upper().strip() for value in stock_symbols if value.strip()}):
        issuer = ticker_map.get(symbol)
        if not issuer:
            continue
        cik = issuer.get("cik", "")
        if not cik:
            continue
        try:
            submission = submission_fetcher(cik, timeout_sec, user_agent)
            recent = submission.get("filings", {}).get("recent", {})
            forms = recent.get("form", []) or []
            dates = recent.get("filingDate", []) or []
            accession_numbers = recent.get("accessionNumber", []) or []
            for form, filing_date, accession_number in zip(forms, dates, accession_numbers):
                if str(form) not in {"4", "4/A"}:
                    continue
                insiders_form4.append(
                    {
                        "symbol": symbol,
                        "issuer": issuer.get("name", symbol),
                        "cik": cik,
                        "form": str(form),
                        "filing_date": str(filing_date),
                        "url": _build_sec_filing_url(cik, str(accession_number)),
                    }
                )
                break
        except Exception as exc:
            print(f"[tradepulse][sec] Form4 fetch failed for {symbol}: {str(exc)}")

    institutions_13f = sorted(institutions_13f, key=lambda item: item.get("filing_date", ""), reverse=True)
    insiders_form4 = sorted(insiders_form4, key=lambda item: item.get("filing_date", ""), reverse=True)
    return {
        "status": "ok",
        "institutions_13f": institutions_13f[:10],
        "insiders_form4": insiders_form4[:10],
    }


def build_market_regime_snapshot(
    options: MarketRegimeOptions,
    us_price_fetcher: Callable[[str, float], List[float]] = fetch_us_prices,
    us_flow_fetcher: Callable[[str, float], Dict[str, Any]] = fetch_us_flow_metrics,
    a_share_fetcher: Callable[[float], Dict[str, Any]] = fetch_a_share_flow,
    sec_disclosure_fetcher: Callable[[List[str], List[str], float, str], Dict[str, Any]] = build_sec_disclosure_snapshot,
) -> Dict[str, Any]:
    if not options.enabled:
        return {}

    snapshot: Dict[str, Any] = {}

    if options.us_enabled:
        us_snapshot: Dict[str, Any] = {}
        try:
            symbols = list(US_BENCHMARK_SYMBOLS) + list(US_SECTOR_NAMES.keys())
            price_map = _fetch_us_price_map(
                symbols=symbols,
                timeout_sec=options.request_timeout_sec,
                price_fetcher=us_price_fetcher,
            )
            ranked = compute_us_sector_rankings(price_map, top_n=options.us_top_n)
            us_snapshot.update(ranked)
            us_snapshot["status"] = "ok"
        except Exception:
            us_snapshot = {
                "status": "unavailable",
                "message": "美股板块强弱数据暂不可用",
            }

        if us_snapshot.get("status") == "ok":
            try:
                sector_flow_map = _fetch_us_flow_map(
                    symbols=list(US_SECTOR_NAMES.keys()),
                    timeout_sec=options.request_timeout_sec,
                    flow_fetcher=us_flow_fetcher,
                )
                us_snapshot["flow_proxy"] = compute_us_flow_proxy_rankings(
                    sector_flow_map,
                    top_n=options.us_top_n,
                )
            except Exception:
                us_snapshot["flow_proxy"] = {"inflow": [], "outflow": []}

            try:
                stock_symbols = [item.upper().strip() for item in options.stock_universe if item.strip()]
                stock_flow_map = _fetch_us_flow_map(
                    symbols=stock_symbols,
                    timeout_sec=options.request_timeout_sec,
                    flow_fetcher=us_flow_fetcher,
                )
                us_snapshot["stock_flow"] = compute_us_flow_proxy_rankings(
                    stock_flow_map,
                    top_n=options.us_stock_flow_top_n,
                )
            except Exception:
                us_snapshot["stock_flow"] = {"inflow": [], "outflow": []}

            try:
                if options.us_market_flow_enabled:
                    market_symbols = fetch_nasdaq_symbols(options.request_timeout_sec)[:options.us_market_flow_universe_size]
                    market_stock_flow_map = _fetch_us_flow_map(
                        symbols=market_symbols,
                        timeout_sec=options.request_timeout_sec,
                        flow_fetcher=us_flow_fetcher,
                    )
                    us_snapshot["market_stock_flow"] = compute_us_flow_proxy_rankings(
                        market_stock_flow_map,
                        top_n=options.us_market_flow_top_n,
                    )
            except Exception:
                us_snapshot["market_stock_flow"] = {"inflow": [], "outflow": []}

        snapshot["us"] = us_snapshot

    if options.a_share_enabled:
        try:
            payload = a_share_fetcher(options.request_timeout_sec)
            if isinstance(payload, dict) and "inflow_payload" in payload and "outflow_payload" in payload:
                inflow_rows = _extract_a_share_entries(payload["inflow_payload"])
                outflow_rows = _extract_a_share_entries(payload["outflow_payload"])
                ranked_flow = {
                    "inflow": sorted(inflow_rows, key=lambda item: item["net_flow"], reverse=True)[: options.a_share_top_n],
                    "outflow": sorted(outflow_rows, key=lambda item: item["net_flow"])[: options.a_share_top_n],
                }
            else:
                ranked_flow = parse_a_share_flow(payload, top_n=options.a_share_top_n)
            if not ranked_flow["inflow"] and not ranked_flow["outflow"]:
                raise ValueError("empty A-share flow rows")
            snapshot["a_share"] = {"status": "ok", **ranked_flow}
        except Exception:
            snapshot["a_share"] = {"status": "unavailable", "message": "A股资金流数据暂不可用"}

    if options.sec_enabled:
        try:
            snapshot["sec"] = sec_disclosure_fetcher(
                options.stock_universe,
                options.sec_13f_ciks,
                options.request_timeout_sec,
                options.sec_user_agent,
            )
        except Exception:
            snapshot["sec"] = {"status": "unavailable", "message": "SEC披露数据暂不可用"}

    return snapshot
