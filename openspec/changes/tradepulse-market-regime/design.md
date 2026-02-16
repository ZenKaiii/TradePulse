## Context

TradePulse currently ships an importance-first news digest, but lacks a structured market-regime view. Traders need this context (leadership rotation and capital flow) to avoid taking setups that conflict with sector-level dynamics.

## Goals / Non-Goals

**Goals:**
- Add Section 4 to digest for market-structure context.
- Compute US sector ranking using SPDR sector ETFs vs SPY/QQQ over 4W and 12W windows.
- Add A-share inflow/outflow ranking based on a low-friction public endpoint.
- Keep pipeline robust with partial-failure tolerance.

**Non-Goals:**
- No intraday signal engine.
- No execution/alert strategy for entry timing.
- No advanced stage-analysis automation in this phase.

## Decisions

1. **Use Stooq daily CSV for US ETF prices**
   - Rationale: no API key required, low integration cost, broad symbol coverage.
   - Alternative considered: yfinance SDK (extra dependency and higher request complexity).

2. **Use Eastmoney push2 endpoint for A-share sector flow**
   - Rationale: direct JSON response with sector name and net flow fields, no auth required.
   - Alternative considered: AkShare dependency (larger dependency surface for MVP).

3. **Isolate logic into `tradepulse.market.regime` module**
   - Rationale: keeps pipeline orchestration simple and testable, avoids coupling scoring/compose code.
   - Alternative considered: embedding logic in `run_once.py` (harder to test/maintain).

4. **Section-level resilience by provider boundary**
   - Rationale: market context is additive; failure must not block core news digest.
   - Alternative considered: hard-fail on any provider error (too brittle for scheduled automation).

## Risks / Trade-offs

- **[External endpoint instability]** → Add timeout, parse guards, and fallback text.
- **[Cross-market holiday/clock skew]** → Use most recent available daily close and avoid strict same-day assumptions.
- **[Ranking noise in choppy markets]** → Expose configurable top/bottom row counts and keep formula transparent.

## Migration Plan

1. Add config schema and default values for market regime.
2. Add market-regime module with data fetchers + ranking functions.
3. Wire pipeline + composer Section 4 rendering.
4. Update workflow variables and docs.
5. Rollback plan: set `market_regime.enabled=false` (or remove env overrides) to disable Section 4 safely.

## Open Questions

- Whether to add a premium provider abstraction for higher-quality A-share flow in future.
- Whether to persist regime snapshots for trend comparisons over multiple runs.
