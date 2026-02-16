# TradePulse Setup

## 1. Local install

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

## 2. Base config file

```bash
cp config/user.example.yaml config/user.yaml
```

Recommended fields in `config/user.yaml`:

- `digest.top_n`
- `sources.profile`
- `sources.tier`
- `sources.min_health_score`
- `watchlists.stocks`
- `watchlists.keywords`
- `watchlists.geopolitics`
- `delivery.channels`
- `market_regime.enabled`
- `market_regime.us_enabled`
- `market_regime.a_share_enabled`
- `market_regime.us_top_n`
- `market_regime.a_share_top_n`
- `market_regime.request_timeout_sec`
- `llm.enabled`
- `llm.provider`
- `llm.detail_top_n`
- `llm.timeout_sec`
- `llm.temperature`
- `llm.bailian_model`
- `llm.bailian_base_url`
- `llm.gemini_model`
- `llm.gemini_base_url`

## 3. Runtime override model

Runtime config priority:

1. `TRADEPULSE_*` environment variables
2. `config/user.yaml`
3. `config/user.example.yaml`

Use this to keep reusable defaults in git and environment-specific changes in GitHub Variables.

## 4. GitHub Actions

Workflow:

- `.github/workflows/hourly.yml`

Schedule:

- every hour (`0 * * * *`)

### 4.1 Secrets (sensitive)

- `BAILIAN_API_KEY` (recommended primary LLM)
- `GEMINI_API_KEY` (optional fallback LLM)
- `DINGTALK_WEBHOOK_URL` (optional)
- `TELEGRAM_BOT_TOKEN` (optional)
- `TELEGRAM_CHAT_ID` (optional)
- `FEISHU_WEBHOOK_URL` (optional)

### 4.2 Variables (non-sensitive)

- `TRADEPULSE_CONFIG_PATH`
- `TRADEPULSE_TOP_N`
- `TRADEPULSE_SOURCE_PROFILE`
- `TRADEPULSE_SOURCE_TIER`
- `TRADEPULSE_MIN_HEALTH_SCORE`
- `TRADEPULSE_STOCKS`
- `TRADEPULSE_KEYWORDS`
- `TRADEPULSE_GEOPOLITICS`
- `TRADEPULSE_CHANNELS`
- `TRADEPULSE_MARKET_ENABLED`
- `TRADEPULSE_MARKET_US_ENABLED`
- `TRADEPULSE_MARKET_A_SHARE_ENABLED`
- `TRADEPULSE_MARKET_US_TOP_N`
- `TRADEPULSE_MARKET_A_SHARE_TOP_N`
- `TRADEPULSE_MARKET_TIMEOUT_SEC`
- `TRADEPULSE_LLM_ENABLED`
- `TRADEPULSE_LLM_PROVIDER`
- `TRADEPULSE_LLM_DETAIL_TOP_N`
- `TRADEPULSE_LLM_TIMEOUT_SEC`
- `TRADEPULSE_LLM_TEMPERATURE`
- `TRADEPULSE_BAILIAN_MODEL`
- `TRADEPULSE_BAILIAN_BASE_URL`
- `TRADEPULSE_GEMINI_MODEL`
- `TRADEPULSE_GEMINI_BASE_URL`

List variables support comma or newline separators.
For LLM defaults, TradePulse uses `qwen-plus` (Bailian) and falls back to `gemini-2.0-flash` when configured.

## 5. Dry run and production run

```bash
# local dry run (no push)
.venv/bin/python -m tradepulse.cli run --dry-run

# production run (push enabled channels)
.venv/bin/python -m tradepulse.cli run
```
