from pathlib import Path

from tradepulse.config import load_user_config


def test_default_top_n_is_10(tmp_path: Path):
    cfg = tmp_path / "user.yaml"
    cfg.write_text("sources:\n  profile: trader\n", encoding="utf-8")

    data = load_user_config(cfg)

    assert data.digest.top_n == 10
    assert data.sources.tier == "core"
