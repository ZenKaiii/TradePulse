from typing import Dict

from tradepulse.notifiers.base import _post_json


def build_payload(text: str) -> Dict:
    return {"msg_type": "text", "content": {"text": text}}


def send(webhook_url: str, text: str) -> None:
    if not webhook_url:
        raise ValueError("feishu webhook url is required")
    _post_json(webhook_url, build_payload(text))
