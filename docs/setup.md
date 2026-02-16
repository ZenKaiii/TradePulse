# TradePulse Setup

## 1. Local Setup

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

## 2. Config

```bash
cp config/user.example.yaml config/user.yaml
```

Edit:
- `watchlists.stocks`
- `watchlists.keywords`
- `watchlists.geopolitics`
- `digest.top_n` (default 10)
- `delivery.channels`

## 3. Dry Run

```bash
.venv/bin/python -m tradepulse.cli run --dry-run
```

## 4. Required/Optional Secrets

LLM (at least one recommended):
- `BAILIAN_API_KEY`
- `GEMINI_API_KEY`

Push channels (optional):
- `DINGTALK_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `FEISHU_WEBHOOK_URL`

## 5. GitHub Actions

Workflow is preconfigured at:
- `.github/workflows/hourly.yml`

Schedule:
- every hour (`0 * * * *`)
