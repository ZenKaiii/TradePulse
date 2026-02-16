# TradePulse

TradePulse is an AI-native, importance-first news aggregation and analysis tool for stock traders.
It runs on GitHub Actions hourly, outputs a Chinese digest, and includes source links for every event.

[中文说明](README.zh-CN.md)

## What It Solves

- Pull high-signal RSS/news sources for traders
- Rank events by importance (Top N)
- Add topic overlays (stocks/keywords/geopolitics) without breaking the main ranking
- Output actionable digest:
  - market direction: `Bullish / Bearish / Neutral`
  - affected tickers and company names
  - short impact reason in Chinese
  - source attribution (`publisher + URL`)
- Push incrementally (new clusters only) to:
  - DingTalk
  - Telegram
  - Feishu

## Architecture (MVP)

1. Ingest RSS feeds by profile + tier
2. Score feed health and keep healthy sources
3. Cluster duplicate coverage by URL fingerprint
4. Rule-score each event (importance + direction + ticker extraction)
5. Build digest (`TopN + overlays`)
6. Use SQLite ledger for incremental push
7. Send to enabled channels

## Quick Start

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
cp config/user.example.yaml config/user.yaml
.venv/bin/python -m tradepulse.cli run --dry-run
```

## Configuration Layers (Priority)

Runtime config priority is:

1. GitHub Actions environment variables (`TRADEPULSE_*`)
2. `config/user.yaml`
3. `config/user.example.yaml` defaults

This lets you keep base config in file and override non-sensitive values in GitHub `Variables`.

## GitHub Actions Setup

Workflow file:

- `.github/workflows/hourly.yml`

Default schedule:

- every hour (`0 * * * *`)

### 1) Add Secrets (sensitive)

| Name | Required | Purpose | Example |
|---|---|---|---|
| `BAILIAN_API_KEY` | Recommended | Primary LLM provider (Alibaba Cloud Bailian) | `sk-***` |
| `GEMINI_API_KEY` | Optional | Fallback LLM provider | `AIza***` |
| `DINGTALK_WEBHOOK_URL` | Optional | DingTalk bot webhook | `https://oapi.dingtalk.com/robot/send?access_token=***` |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram bot token from BotFather | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Optional | Telegram target chat id | `-1001234567890` |
| `FEISHU_WEBHOOK_URL` | Optional | Feishu bot webhook | `https://open.feishu.cn/open-apis/bot/v2/hook/***` |

Notes:

- At least one push channel secret should be configured if you want delivery.
- If both `BAILIAN_API_KEY` and `GEMINI_API_KEY` are set, Bailian is preferred.

### 2) Add Variables (non-sensitive)

| Name | Required | Purpose | Example |
|---|---|---|---|
| `TRADEPULSE_CONFIG_PATH` | Optional | Custom config path (repo-relative or absolute) | `config/user.yaml` |
| `TRADEPULSE_TOP_N` | Optional | Digest Top N (1-50) | `10` |
| `TRADEPULSE_SOURCE_PROFILE` | Optional | Source profile | `trader` |
| `TRADEPULSE_SOURCE_TIER` | Optional | Source tier (`core/extended/experimental`) | `core` |
| `TRADEPULSE_MIN_HEALTH_SCORE` | Optional | Feed health filter (0-100) | `30` |
| `TRADEPULSE_STOCKS` | Optional | Overlay stock list (comma-separated) | `NVDA,AAPL,MSFT` |
| `TRADEPULSE_KEYWORDS` | Optional | Overlay keywords (comma-separated) | `fed rate cut,treasury yield` |
| `TRADEPULSE_GEOPOLITICS` | Optional | Overlay geopolitics topics (comma-separated) | `middle-east,us-china-tech` |
| `TRADEPULSE_CHANNELS` | Optional | Enabled channels (comma-separated) | `dingtalk,telegram` |

List-type variables support comma or newline separators.

### 3) Channel-specific setup

- DingTalk:
  - Create group bot and copy webhook URL to `DINGTALK_WEBHOOK_URL`.
- Telegram:
  - Create bot with BotFather and get token (`TELEGRAM_BOT_TOKEN`).
  - Add bot to target chat/group.
  - Fetch `chat_id` via Telegram Bot API and set `TELEGRAM_CHAT_ID`.
- Feishu:
  - Create custom bot and copy webhook URL to `FEISHU_WEBHOOK_URL`.

## Source Tiers

- `core`: default high-signal feeds
- `extended`: `core` + broader coverage
- `experimental`: `extended` + long-tail feeds

Use `sources.min_health_score` (or `TRADEPULSE_MIN_HEALTH_SCORE`) to skip low-health feeds.

## Output Format

1. A. 本小时关键事件 TopN
2. B. 专题命中（股票 / 关键词 / 地缘）
3. Each event includes direction, affected stock(s), impact note, and sources

## Run Commands

```bash
# dry run (no push)
.venv/bin/python -m tradepulse.cli run --dry-run

# real run (push to enabled channels)
.venv/bin/python -m tradepulse.cli run
```

## Disclaimer

TradePulse is for research and workflow automation only, not financial advice.
