from typing import Dict

from tradepulse.notifiers.base import _post_json


def _chunk_text(text: str, limit: int = 3500) -> list[str]:
    stripped = (text or "").strip()
    if not stripped:
        return [""]
    if len(stripped) <= limit:
        return [stripped]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in stripped.splitlines():
        line_len = len(line) + 1
        if current and current_len + line_len > limit:
            chunks.append("\n".join(current).strip())
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len

    if current:
        chunks.append("\n".join(current).strip())
    return [chunk for chunk in chunks if chunk] or [stripped[:limit]]


def build_payload(bot_token: str, chat_id: str, text: str) -> Dict:
    return {
        "url": f"https://api.telegram.org/bot{bot_token}/sendMessage",
        "json": {"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
    }


def send(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        raise ValueError("telegram token and chat_id are required")
    for chunk in _chunk_text(text):
        payload = build_payload(bot_token, chat_id, chunk)
        _post_json(payload["url"], payload["json"])
