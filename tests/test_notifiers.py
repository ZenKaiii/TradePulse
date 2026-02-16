from tradepulse.notifiers.dingtalk import build_payload as build_dingtalk_payload
from tradepulse.notifiers.feishu import build_payload as build_feishu_payload
from tradepulse.notifiers.telegram import build_payload as build_telegram_payload


def test_dingtalk_payload_contains_text():
    payload = build_dingtalk_payload("hello")
    assert payload["msgtype"] == "text"
    assert payload["text"]["content"] == "hello"


def test_telegram_payload_contains_text():
    payload = build_telegram_payload("bot-token", "chat-id", "hello")
    assert payload["url"].endswith("/sendMessage")
    assert payload["json"]["text"] == "hello"


def test_feishu_payload_contains_text():
    payload = build_feishu_payload("hello")
    assert payload["msg_type"] == "text"
    assert payload["content"]["text"] == "hello"
