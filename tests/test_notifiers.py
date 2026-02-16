from tradepulse.notifiers.dingtalk import build_payload as build_dingtalk_payload
from tradepulse.notifiers.feishu import build_payload as build_feishu_payload
from tradepulse.notifiers.telegram import build_payload as build_telegram_payload
from tradepulse.notifiers import telegram as telegram_notifier


def test_dingtalk_payload_contains_text():
    payload = build_dingtalk_payload("hello")
    assert payload["msgtype"] == "markdown"
    assert payload["markdown"]["title"] == "TradePulse 每小时快报"
    assert payload["markdown"]["text"] == "hello"


def test_telegram_payload_contains_text():
    payload = build_telegram_payload("bot-token", "chat-id", "hello")
    assert payload["url"].endswith("/sendMessage")
    assert payload["json"]["text"] == "hello"
    assert payload["json"]["parse_mode"] == "Markdown"


def test_telegram_send_splits_long_message(monkeypatch):
    sent_texts = []

    def _fake_post(url, payload):
        sent_texts.append(payload["text"])

    monkeypatch.setattr(telegram_notifier, "_post_json", _fake_post)
    very_long = "\n".join([f"line-{idx}" for idx in range(1200)])
    telegram_notifier.send("bot-token", "chat-id", very_long)

    assert len(sent_texts) >= 2
    assert all(len(item) <= 3500 for item in sent_texts)


def test_telegram_send_falls_back_to_plain_text_when_markdown_fails(monkeypatch):
    calls = []

    def _fake_post(url, payload):
        calls.append(payload)
        if len(calls) == 1:
            raise RuntimeError("Bad Request: can't parse entities")

    monkeypatch.setattr(telegram_notifier, "_post_json", _fake_post)
    telegram_notifier.send("bot-token", "chat-id", "# Header\n- item")

    assert len(calls) == 2
    assert calls[0].get("parse_mode") == "Markdown"
    assert "parse_mode" not in calls[1]


def test_feishu_payload_contains_text():
    payload = build_feishu_payload("hello")
    assert payload["msg_type"] == "text"
    assert payload["content"]["text"] == "hello"
