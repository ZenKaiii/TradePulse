## Context

TradePulse currently provides relative strength and A-share flow but not US daily flow proxy or disclosure-tracking context. Telegram delivery works but lacks rich formatting. External search augmentation is absent.

## Decisions

1. **US flow proxy**
- Use free OHLCV-derived proxy (`dollar_volume * daily_return`) for sector ETFs and stock universe.
- Clearly label as proxy (not true order-flow tape).

2. **Disclosure tracking**
- Institutions: configurable 13F CIK watchlist with sensible defaults.
- Insiders: Form4 based on watchlist symbols mapped to CIK.
- SEC calls require `User-Agent`; any failure degrades gracefully.

3. **Search enhancement**
- Add optional Tavily integration (off by default), only for top detailed events.
- Add best-effort behavior and stats.

4. **Telegram formatting**
- Enable Markdown parse mode and heading formatting.
- On parse failure, fallback to plain text to guarantee delivery.

5. **Source expansion**
- Add Google News RSS in extended tier to broaden topical coverage.

## Risks

- SEC/API rate limits -> keep request fan-out bounded and catch failures.
- Proxy interpretation confusion -> explicit explanatory copy.
- Tavily cost latency -> opt-in + top-n only.
