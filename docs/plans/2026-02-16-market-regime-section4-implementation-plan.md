# Section 4 Market Regime Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Section 4 market-structure output (US sector rotation + A-share flow ranking) into TradePulse digest.

**Architecture:** Implement isolated market-regime module, wire config and pipeline integration, then extend digest rendering with robust fallback behavior.

**Tech Stack:** Python 3.8+, httpx, pytest, OpenSpec

---

### Task 1: Add failing tests

**Files:**
- Create: `tests/test_market_regime.py`
- Modify: `tests/test_compose.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_pipeline_run_once.py`

1. Write tests for US ranking, A-share parsing, and failure fallback.
2. Run targeted tests and confirm failure.

### Task 2: Implement market-regime module

**Files:**
- Create: `src/tradepulse/market/__init__.py`
- Create: `src/tradepulse/market/regime.py`

1. Add fetchers for Stooq and Eastmoney.
2. Add ranking/parsing functions.
3. Add resilient snapshot builder.

### Task 3: Wire config and pipeline

**Files:**
- Modify: `src/tradepulse/config.py`
- Modify: `src/tradepulse/pipeline/run_once.py`
- Modify: `config/user.example.yaml`

1. Add `market_regime` model and parser defaults.
2. Add env overrides for `TRADEPULSE_MARKET_*`.
3. Build snapshot in pipeline and pass to composer.

### Task 4: Extend digest rendering

**Files:**
- Modify: `src/tradepulse/compose.py`

1. Render Section 4 text for US/A-share.
2. Render fallback message when unavailable.

### Task 5: Update workflow and docs

**Files:**
- Modify: `.github/workflows/hourly.yml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/setup.md`

1. Add new market-related GitHub Variables.
2. Document usage and data sources.

### Task 6: Verify and finalize

**Files:**
- Modify: `openspec/changes/tradepulse-market-regime/tasks.md`

1. Run full `pytest`.
2. Run `openspec validate tradepulse-market-regime --type change`.
3. Mark OpenSpec tasks complete.
