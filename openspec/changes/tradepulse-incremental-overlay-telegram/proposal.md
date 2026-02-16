## Why

Latest run still repeats the same Top10 and misses expected watchlist/telegram behavior:
- Section A repeats old events because digest body is not filtered by incremental ledger.
- Section A quality is skewed by stale and single-source items.
- Section B overlays do substring matching on Top10-only titles, causing misses and false positives.
- Telegram credentials are present but channel is not enabled when `TRADEPULSE_CHANNELS` is empty.

## What Changes

- Make Section A strictly incremental from ledger state and show explicit "no new events" when none.
- Add freshness and source-cap controls for event selection.
- Upgrade overlay engine to structured, boundary-aware matching across candidate events.
- Auto-detect delivery channels from configured credentials when channels are not explicitly set.
- Enhance Section C with sector-rotation watchlist ideas (education-only, not investment advice).

## Capabilities

### New Capabilities
- `incremental-hourly-digest`: no-repeat event push behavior with clear no-new messaging.
- `delivery-channel-autodetect`: automatic notifier channel activation from credentials.
- `sector-rotation-watchlist-ideas`: convert sector leadership into actionable observation checklist.

### Modified Capabilities
- `topic-overlay-monitoring`: richer and more accurate overlay hits with event-level evidence.

## Impact

- `src/tradepulse/pipeline/run_once.py`
- `src/tradepulse/overlays.py`
- `src/tradepulse/compose.py`
- `src/tradepulse/config.py`
- `tests/test_pipeline_run_once.py`
- `tests/test_overlays.py`
- `tests/test_compose.py`
- `README.md`, `README.zh-CN.md`, `config/user.example.yaml`
