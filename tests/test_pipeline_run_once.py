from tradepulse.models import CanonicalArticle
import importlib
from tradepulse.pipeline.run_once import _collect_senders, resolve_channels, run_once
from tradepulse.sources import FeedHealth

run_once_module = importlib.import_module("tradepulse.pipeline.run_once")


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


def test_resolve_channels_auto_adds_telegram_when_unset(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")
    monkeypatch.delenv("TRADEPULSE_CHANNELS", raising=False)

    channels = resolve_channels(["dingtalk"])
    assert channels == ["dingtalk", "telegram"]


def test_run_once_only_shows_incremental_events(monkeypatch, tmp_path):
    monkeypatch.setattr(run_once_module, "_project_root", lambda: tmp_path)
    monkeypatch.setenv("TRADEPULSE_MARKET_ENABLED", "false")
    monkeypatch.setenv("TRADEPULSE_LLM_ENABLED", "false")
    monkeypatch.setenv("TRADEPULSE_CHANNELS", "")

    now_article = CanonicalArticle(
        id="1",
        title="NVDA raises AI guidance",
        url="https://example.com/nvda-guidance",
        source_name="CNBC",
        published_at="Mon, 16 Feb 2026 11:00:00 GMT",
        summary_raw="",
    )
    stale_article = CanonicalArticle(
        id="2",
        title="Old regulatory approval item",
        url="https://example.com/old-fed-item",
        source_name="Federal Reserve",
        published_at="Mon, 12 Jan 2026 11:00:00 GMT",
        summary_raw="",
    )

    def _fetch(*args, **kwargs):
        return (
            [now_article, stale_article],
            [
                FeedHealth(
                    name="CNBC",
                    url="https://example.com/cnbc",
                    tier="core",
                    ok=True,
                    entry_count=1,
                    health_score=95,
                ),
                FeedHealth(
                    name="Federal Reserve",
                    url="https://example.com/fed",
                    tier="core",
                    ok=True,
                    entry_count=1,
                    health_score=95,
                ),
            ],
        )

    monkeypatch.setattr(run_once_module, "fetch_articles_with_health", _fetch)
    monkeypatch.setattr(run_once_module, "send_best_effort", lambda senders: [])

    first = run_once(dry_run=False)
    assert first["stats"]["new_events"] == 1
    assert "NVDA raises AI guidance" in first["digest"]

    second = run_once(dry_run=False)
    assert second["stats"]["new_events"] == 0
    assert "本小时无新增关键事件" in second["digest"]
