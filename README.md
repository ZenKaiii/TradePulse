# TradePulse

TradePulse is an AI-native, importance-first news digest tool for US stock traders.
It runs hourly (GitHub Actions), outputs Chinese summaries, and always includes source links.

## Features

- Hourly `Top10` key events by importance
- Topic overlays (stocks/keywords/geopolitics) as append-only sections
- Chinese digest with:
  - `利好 / 利空 / 中性`
  - affected ticker and company name
  - source attribution (publisher + URL)
- LLM routing by secrets:
  - Bailian preferred
  - Gemini fallback
- Multi-channel push:
  - DingTalk
  - Telegram
  - Feishu

## Quick Start

1. Copy config template:
   - `cp config/user.example.yaml config/user.yaml`
2. Edit watchlists and channels in `config/user.yaml`.
3. Dry run locally:
   - `.venv/bin/python -m tradepulse.cli run --dry-run`

## GitHub Secrets

LLM:
- `BAILIAN_API_KEY` (primary)
- `GEMINI_API_KEY` (fallback)

Channels:
- `DINGTALK_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `FEISHU_WEBHOOK_URL`

## Run Schedule

Workflow file: `.github/workflows/hourly.yml`

- Cron: every hour (`0 * * * *`)
- Supports manual trigger via `workflow_dispatch`

## Output Structure

1. A. 本小时关键事件 Top10
2. B. 专题命中（股票/关键词/地缘）
3. 每条事件包含方向、标的、影响说明、来源
