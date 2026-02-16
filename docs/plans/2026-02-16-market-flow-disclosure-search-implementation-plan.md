# Market Flow + Disclosures + Tavily Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 TradePulse 增加可配置的搜索增强、Section4 美股资金流代理、机构13F与内部人Form4追踪，并修正默认模型与Telegram格式化。

**Architecture:** 通过配置层扩展 + market/regime 数据聚合 + compose 展示增强 + notifier 容错实现端到端功能，保持主链路在外部源失败时可降级。

**Tech Stack:** Python 3.11, httpx, urllib, pytest, OpenSpec, GitHub Actions

---

### Task 1: 配置与默认值（模型/搜索/市场参数）
**Files:**
- Modify: `src/tradepulse/config.py`
- Modify: `config/user.example.yaml`
- Test: `tests/test_config.py`

### Task 2: Telegram Markdown 与回退
**Files:**
- Modify: `src/tradepulse/notifiers/telegram.py`
- Test: `tests/test_notifiers.py`

### Task 3: Tavily 可选增强
**Files:**
- Create: `src/tradepulse/search/__init__.py`
- Create: `src/tradepulse/search/tavily.py`
- Modify: `src/tradepulse/pipeline/run_once.py`
- Modify: `src/tradepulse/compose.py`
- Test: `tests/test_search_tavily.py`

### Task 4: Section4 美股资金流代理
**Files:**
- Modify: `src/tradepulse/market/regime.py`
- Modify: `src/tradepulse/pipeline/run_once.py`
- Modify: `src/tradepulse/compose.py`
- Test: `tests/test_market_regime.py`

### Task 5: 13F + Form4 披露追踪
**Files:**
- Modify: `src/tradepulse/market/regime.py`
- Modify: `src/tradepulse/pipeline/run_once.py`
- Modify: `src/tradepulse/compose.py`
- Test: `tests/test_market_regime.py`

### Task 6: Google News RSS 接入
**Files:**
- Modify: `src/tradepulse/sources.py`
- Test: `tests/test_sources.py` (new if needed)

### Task 7: 文档与OpenSpec
**Files:**
- Create: `openspec/changes/tradepulse-market-flow-disclosure-search/*`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `.github/workflows/hourly.yml`

### Task 8: 验证与提交
- Run: `uv run --with pytest pytest -q`
- Run: `openspec validate tradepulse-market-flow-disclosure-search --type change`
- Commit + push + merge to `main`
