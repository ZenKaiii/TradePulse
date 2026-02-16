# TradePulse Section 4 Market Regime Design

## Context

TradePulse currently outputs event-level digest sections but lacks sector-rotation and capital-flow context.
Section 4 adds a repeatable market-structure view for traders.

## Goals

- Add US sector relative-strength ranking (4W/12W vs SPY+QQQ).
- Add A-share sector fund-flow ranking (inflow/outflow leaders).
- Keep digest resilient when one data provider fails.

## Non-Goals

- No intraday signal generation.
- No execution strategy automation.
- No historical snapshot persistence in this phase.

## Architecture

- New module: `src/tradepulse/market/regime.py`
- Config: `market_regime.*` in user config + `TRADEPULSE_MARKET_*` env overrides
- Pipeline: build snapshot in `run_once` and pass into `compose_digest`
- Composer: render new Section 4 block with fallback text

## Data Sources

- US ETF prices: Stooq daily CSV
- A-share flow: Eastmoney push2 sector ranking endpoint

## Resilience

- US and A-share sub-sections are independent.
- Failure in one data provider does not block digest generation.
