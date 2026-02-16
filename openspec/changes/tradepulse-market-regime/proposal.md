## Why

TradePulse currently focuses on event-level news, but traders also need market-structure context (sector leadership and capital flow) to avoid trading against rotation. Adding a dedicated Section 4 provides a repeatable top-down view each run.

## What Changes

- Add a new digest section for market regime insights (US sector relative strength + A-share sector fund flow rankings).
- Compute US sector rankings from 4-week and 12-week relative strength versus SPY and QQQ.
- Pull A-share sector fund flow rankings (inflow/outflow leaders) and include the top entries.
- Make market-regime generation resilient: if one provider fails, digest still delivers with available sub-sections.
- Add user-facing configuration knobs for enabling/disabling Section 4 and controlling row counts.

## Capabilities

### New Capabilities
- `market-regime-section`: Generate and append trader-focused market-structure output (US rotation + A-share flow).

### Modified Capabilities
- None.

## Impact

- `src/tradepulse/config.py`: Add market-regime config model and parser support.
- `src/tradepulse/pipeline/run_once.py`: Build and pass Section 4 payload into composer.
- `src/tradepulse/compose.py`: Render Section 4 in digest output.
- `src/tradepulse/market/*`: New module for data fetching, scoring, ranking, and formatting payloads.
- `tests/*`: Add unit tests for ranking logic, resilience behavior, and digest rendering.
- `README.md`, `README.zh-CN.md`, `docs/setup.md`, `.github/workflows/hourly.yml`: Document and wire new runtime variables.
