from pathlib import Path

from tradepulse.config import apply_env_overrides, load_user_config


def test_default_top_n_is_10(tmp_path: Path):
    cfg = tmp_path / "user.yaml"
    cfg.write_text("sources:\n  profile: trader\n", encoding="utf-8")

    data = load_user_config(cfg)

    assert data.digest.top_n == 10
    assert data.sources.tier == "core"


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
        },
    )

    assert runtime.digest.top_n == 12
    assert runtime.sources.tier == "extended"
    assert runtime.sources.min_health_score == 45
    assert runtime.watchlists.stocks == ["AAPL", "MSFT"]
    assert runtime.watchlists.keywords == ["fed rate cut", "treasury yield"]
    assert runtime.watchlists.geopolitics == ["taiwan strait"]
    assert runtime.delivery.channels == ["telegram", "feishu"]
