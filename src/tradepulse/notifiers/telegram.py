from typing import Dict

from tradepulse.notifiers.base import _post_json


def build_payload(bot_token: str, chat_id: str, text: str) -> Dict:
    return {
        "url": f"https://api.telegram.org/bot{bot_token}/sendMessage",
        "json": {"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
    }


def send(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        raise ValueError("telegram token and chat_id are required")
    payload = build_payload(bot_token, chat_id, text)
    _post_json(payload["url"], payload["json"])
