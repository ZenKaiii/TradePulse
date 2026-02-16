from tradepulse.pipeline.run_once import _collect_senders, run_once


def test_run_once_returns_digest_and_stats(monkeypatch):
    monkeypatch.setenv("TRADEPULSE_MARKET_ENABLED", "false")
    monkeypatch.setenv("TRADEPULSE_LLM_ENABLED", "false")
    result = run_once(dry_run=True)
    assert "digest" in result
    assert "stats" in result


def test_collect_senders_respects_channel_selection(monkeypatch):
    monkeypatch.setenv("DINGTALK_WEBHOOK_URL", "https://example.com/dingtalk")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")
    monkeypatch.setenv("FEISHU_WEBHOOK_URL", "https://example.com/feishu")

    selected = _collect_senders("hello", ["telegram"])
    assert len(selected) == 1
