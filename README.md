# TradePulse

TradePulse is an AI-native, importance-first news aggregation and analysis tool for stock traders.
It runs on GitHub Actions hourly, outputs a Chinese digest, and includes source links for every event.

[中文说明](README.zh-CN.md)

## What It Solves

- Pull high-signal RSS/news sources for traders
- Rank events by importance (Top N)
- Add topic overlays (stocks/keywords/geopolitics) without breaking the main ranking
- Add market-regime section (US sector rotation + US flow proxy + A-share sector flow + SEC disclosures)
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
4. Rule-score each event (importance + seed direction/ticker)
5. LLM enrich each top event:
   - Top5 detailed Chinese analysis
   - Next5 brief Chinese analysis
   - Bailian primary, Gemini fallback
6. Event selection guardrails:
   - incremental-only for Section A (no repeat clusters)
   - freshness filter (`max_age_hours`)
   - source cap (`max_per_source`)
7. Build market-regime snapshot:
   - US: 11 SPDR sector ETFs relative strength (`4W/12W` vs `SPY + QQQ`)
   - US: sector/stock daily flow proxy (`dollar_volume * daily_return`)
   - US: institution 13F + insider Form4 disclosure tracking
   - A-share: sector inflow/outflow ranking
8. Optional search enhancement:
   - Tavily enriches top detailed events with external context (disabled by default)
9. Build digest (`TopN + overlays + Section 4`)
10. Use SQLite ledger for incremental push
11. Send to enabled channels (explicit channels first, else auto-detect from credentials)

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
| `TAVILY_API_KEY` | Optional | Tavily search API key (for optional search enhancement) | `tvly-***` |

Notes:

- At least one push channel secret should be configured if you want delivery.
- If both `BAILIAN_API_KEY` and `GEMINI_API_KEY` are set, Bailian is preferred.

### 2) Add Variables (non-sensitive)

| Name | Required | Purpose | Example |
|---|---|---|---|
| `TRADEPULSE_CONFIG_PATH` | Optional | Custom config path (repo-relative or absolute) | `config/user.yaml` |
| `TRADEPULSE_TOP_N` | Optional | Digest Top N (1-50) | `10` |
| `TRADEPULSE_MAX_AGE_HOURS` | Optional | Keep events newer than this age (hours) | `72` |
| `TRADEPULSE_MAX_PER_SOURCE` | Optional | Max rows per source in Section A | `3` |
| `TRADEPULSE_SOURCE_PROFILE` | Optional | Source profile | `trader` |
| `TRADEPULSE_SOURCE_TIER` | Optional | Source tier (`core/extended/experimental`) | `core` |
| `TRADEPULSE_MIN_HEALTH_SCORE` | Optional | Feed health filter (0-100) | `30` |
| `TRADEPULSE_STOCKS` | Optional | Overlay stock list (comma-separated) | `NVDA,AAPL,MSFT` |
| `TRADEPULSE_KEYWORDS` | Optional | Overlay keywords (comma-separated) | `fed rate cut,treasury yield` |
| `TRADEPULSE_GEOPOLITICS` | Optional | Overlay geopolitics topics (comma-separated) | `middle-east,us-china-tech` |
| `TRADEPULSE_CHANNELS` | Optional | Enabled channels (comma-separated) | `dingtalk,telegram` |
| `TRADEPULSE_MARKET_ENABLED` | Optional | Enable/disable Section 4 | `true` |
| `TRADEPULSE_MARKET_US_ENABLED` | Optional | Enable US sector rotation | `true` |
| `TRADEPULSE_MARKET_A_SHARE_ENABLED` | Optional | Enable A-share flow ranking | `true` |
| `TRADEPULSE_MARKET_US_TOP_N` | Optional | US leaders/laggards row count | `3` |
| `TRADEPULSE_MARKET_US_STOCK_FLOW_TOP_N` | Optional | US stock flow-proxy rows | `5` |
| `TRADEPULSE_MARKET_US_MARKET_FLOW_ENABLED` | Optional | Enable US market stock flow TopN | `true` |
| `TRADEPULSE_MARKET_US_MARKET_FLOW_TOP_N` | Optional | US market stock flow TopN rows | `10` |
| `TRADEPULSE_MARKET_US_MARKET_FLOW_UNIVERSE_SIZE` | Optional | US market stock flow universe size (10-100) | `30` |
| `TRADEPULSE_MARKET_A_SHARE_TOP_N` | Optional | A-share inflow/outflow row count | `5` |
| `TRADEPULSE_MARKET_TIMEOUT_SEC` | Optional | Market data request timeout (1-30 sec) | `8` |
| `TRADEPULSE_MARKET_SEC_ENABLED` | Optional | Enable SEC disclosure tracking | `true` |
| `TRADEPULSE_MARKET_SEC_13F_CIKS` | Optional | Institution 13F CIK list (comma-separated) | `0001067983,0001350694` |
| `TRADEPULSE_SEC_USER_AGENT` | Optional | SEC API User-Agent with contact | `TradePulse/0.1 (contact: you@example.com)` |
| `TRADEPULSE_LLM_ENABLED` | Optional | Enable LLM analysis | `true` |
| `TRADEPULSE_LLM_PROVIDER` | Optional | `auto/bailian/gemini` | `auto` |
| `TRADEPULSE_LLM_DETAIL_TOP_N` | Optional | Detailed analysis rows | `5` |
| `TRADEPULSE_LLM_TIMEOUT_SEC` | Optional | LLM request timeout (5-240 sec, recommended 90s for thinking models) | `90` |
| `TRADEPULSE_LLM_MAX_RETRIES` | Optional | LLM max retries (0-5) | `1` |
| `TRADEPULSE_LLM_RETRY_BACKOFF_SEC` | Optional | LLM retry backoff seconds (0.2-10) | `1.0` |
| `TRADEPULSE_LLM_TEMPERATURE` | Optional | LLM temperature | `0.2` |
| `TRADEPULSE_BAILIAN_MODEL` | Optional | Bailian model name | `qwen3.5-plus` |
| `TRADEPULSE_BAILIAN_BASE_URL` | Optional | Bailian OpenAI-compatible base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `TRADEPULSE_GEMINI_MODEL` | Optional | Gemini model name | `gemini-3-pro-preview` |
| `TRADEPULSE_GEMINI_BASE_URL` | Optional | Gemini API base URL | `https://generativelanguage.googleapis.com/v1beta` |
| `TRADEPULSE_SEARCH_ENABLED` | Optional | Enable search enhancement | `false` |
| `TRADEPULSE_SEARCH_PROVIDER` | Optional | Search provider (`tavily`) | `tavily` |
| `TRADEPULSE_SEARCH_TOP_N` | Optional | Number of detailed events to enrich | `3` |
| `TRADEPULSE_SEARCH_MAX_RESULTS` | Optional | Tavily max results per query | `3` |
| `TRADEPULSE_SEARCH_TIMEOUT_SEC` | Optional | Search request timeout | `12` |

List-type variables support comma or newline separators.

If `TRADEPULSE_CHANNELS` is empty, TradePulse auto-detects channels from credentials:
- `DINGTALK_WEBHOOK_URL` -> `dingtalk`
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` -> `telegram`
- `FEISHU_WEBHOOK_URL` -> `feishu`

### 3) Channel-specific setup

- DingTalk:
  - Create group bot and copy webhook URL to `DINGTALK_WEBHOOK_URL`.
  - TradePulse sends `msgtype=markdown` so headings/lists are rendered in DingTalk.
- Telegram:
  - Create bot with BotFather and get token (`TELEGRAM_BOT_TOKEN`).
  - Add bot to target chat/group.
  - Fetch `chat_id` via Telegram Bot API and set `TELEGRAM_CHAT_ID`.
  - Long digests are auto-split into multiple Telegram messages to avoid length-limit drops.
  - TradePulse sends Telegram with markdown parse mode and falls back to plain text if parsing fails.
- Feishu:
  - Create custom bot and copy webhook URL to `FEISHU_WEBHOOK_URL`.

## Source Tiers

- `core`: default high-signal feeds
- `extended`: `core` + broader coverage (includes Google News business/market feeds)
- `experimental`: `extended` + long-tail feeds

Use `sources.min_health_score` (or `TRADEPULSE_MIN_HEALTH_SCORE`) to skip low-health feeds.

## Output Format

1. A. 本小时关键事件 TopN（Top5 detailed + next5 brief, Chinese AI explanation）
2. B. 专题命中（股票 / 关键词 / 地缘）
3. C. Section 4 板块轮动与资金流（US/A-share + SEC disclosures）
4. Each event includes direction, affected stock(s), impact note, and sources
5. If there is no incremental event in this run, Section A shows a clear “no new key events” message

## LLM Sources

- Bailian (OpenAI-compatible): `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Gemini API: `https://generativelanguage.googleapis.com/v1beta`

## Market Data Sources

- US ETF history: Stooq daily CSV endpoint (`stooq.com`)
- A-share sector flow: Eastmoney push2 industry ranking endpoint (`push2.eastmoney.com`)
- SEC disclosures: `data.sec.gov/submissions` (13F / Form4)
- Optional search context: Tavily Search API (`api.tavily.com`)

## Run Commands

```bash
# dry run (no push)
.venv/bin/python -m tradepulse.cli run --dry-run

# real run (push to enabled channels)
.venv/bin/python -m tradepulse.cli run
```

## Incremental State in GitHub Actions

`data/state.db` is restored/saved with Actions cache in `.github/workflows/hourly.yml`, so incremental dedup works across hourly runs.

## Disclaimer

TradePulse is for research and workflow automation only, not financial advice.
