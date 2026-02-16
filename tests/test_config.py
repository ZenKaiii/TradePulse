from pathlib import Path

from tradepulse.config import apply_env_overrides, load_user_config


def test_default_top_n_is_10(tmp_path: Path):
    cfg = tmp_path / "user.yaml"
    cfg.write_text("sources:\n  profile: trader\n", encoding="utf-8")

    data = load_user_config(cfg)

    assert data.digest.top_n == 10
    assert data.sources.tier == "core"
    assert data.market_regime.enabled is True
    assert data.market_regime.us_top_n == 3
    assert data.market_regime.a_share_top_n == 5
    assert data.llm.enabled is True
    assert data.llm.detail_top_n == 5
    assert data.llm.bailian_model == "qwen-plus"


def test_env_overrides_apply_to_runtime_config(tmp_path: Path):
    cfg = tmp_path / "user.yaml"
    cfg.write_text(
        (
            "digest:\n"
            "  top_n: 8\n"
            "sources:\n"
            "  profile: trader\n"
            "  tier: core\n"
            "  min_health_score: 30\n"
            "watchlists:\n"
            "  stocks: [NVDA]\n"
            "  keywords: [inflation]\n"
            "  geopolitics: [middle-east]\n"
            "delivery:\n"
            "  channels: [dingtalk]\n"
            "market_regime:\n"
            "  enabled: true\n"
            "  us_enabled: true\n"
            "  a_share_enabled: true\n"
            "  us_top_n: 3\n"
            "  a_share_top_n: 5\n"
            "  request_timeout_sec: 8\n"
            "llm:\n"
            "  enabled: true\n"
            "  provider: auto\n"
            "  detail_top_n: 5\n"
            "  temperature: 0.2\n"
            "  timeout_sec: 20\n"
            "  bailian_model: qwen-plus\n"
            "  bailian_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1\n"
            "  gemini_model: gemini-2.0-flash\n"
            "  gemini_base_url: https://generativelanguage.googleapis.com/v1beta\n"
        ),
        encoding="utf-8",
    )
    base = load_user_config(cfg)
    runtime = apply_env_overrides(
        base,
        {
            "TRADEPULSE_TOP_N": "12",
            "TRADEPULSE_SOURCE_TIER": "extended",
            "TRADEPULSE_MIN_HEALTH_SCORE": "45",
            "TRADEPULSE_STOCKS": "AAPL,MSFT",
            "TRADEPULSE_KEYWORDS": "fed rate cut, treasury yield",
            "TRADEPULSE_GEOPOLITICS": "taiwan strait",
            "TRADEPULSE_CHANNELS": "telegram,feishu",
            "TRADEPULSE_MARKET_ENABLED": "false",
            "TRADEPULSE_MARKET_US_ENABLED": "false",
            "TRADEPULSE_MARKET_A_SHARE_ENABLED": "true",
            "TRADEPULSE_MARKET_US_TOP_N": "4",
            "TRADEPULSE_MARKET_A_SHARE_TOP_N": "6",
            "TRADEPULSE_MARKET_TIMEOUT_SEC": "12.5",
            "TRADEPULSE_LLM_ENABLED": "true",
            "TRADEPULSE_LLM_PROVIDER": "bailian",
            "TRADEPULSE_LLM_DETAIL_TOP_N": "4",
            "TRADEPULSE_LLM_TIMEOUT_SEC": "25",
            "TRADEPULSE_LLM_TEMPERATURE": "0.15",
            "TRADEPULSE_BAILIAN_MODEL": "qwen-max",
            "TRADEPULSE_BAILIAN_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "TRADEPULSE_GEMINI_MODEL": "gemini-2.5-flash",
            "TRADEPULSE_GEMINI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta",
        },
    )

    assert runtime.digest.top_n == 12
    assert runtime.sources.tier == "extended"
    assert runtime.sources.min_health_score == 45
    assert runtime.watchlists.stocks == ["AAPL", "MSFT"]
    assert runtime.watchlists.keywords == ["fed rate cut", "treasury yield"]
    assert runtime.watchlists.geopolitics == ["taiwan strait"]
    assert runtime.delivery.channels == ["telegram", "feishu"]
    assert runtime.market_regime.enabled is False
    assert runtime.market_regime.us_enabled is False
    assert runtime.market_regime.a_share_enabled is True
    assert runtime.market_regime.us_top_n == 4
    assert runtime.market_regime.a_share_top_n == 6
    assert runtime.market_regime.request_timeout_sec == 12.5
    assert runtime.llm.enabled is True
    assert runtime.llm.provider == "bailian"
    assert runtime.llm.detail_top_n == 4
    assert runtime.llm.timeout_sec == 25.0
    assert runtime.llm.temperature == 0.15
    assert runtime.llm.bailian_model == "qwen-max"
    assert runtime.llm.gemini_model == "gemini-2.5-flash"
