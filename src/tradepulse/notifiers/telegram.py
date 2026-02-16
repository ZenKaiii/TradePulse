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


def _to_telegram_markdown(text: str) -> str:
    out = []
    for line in str(text or "").splitlines():
        if line.startswith("### "):
            out.append(f"*{line[4:].strip()}*")
        elif line.startswith("## "):
            out.append(f"*{line[3:].strip()}*")
        elif line.startswith("# "):
            out.append(f"*{line[2:].strip()}*")
        else:
            out.append(line)
    return "\n".join(out)


def build_payload(bot_token: str, chat_id: str, text: str) -> Dict:
    return {
        "url": f"https://api.telegram.org/bot{bot_token}/sendMessage",
        "json": {
            "chat_id": chat_id,
            "text": _to_telegram_markdown(text),
            "disable_web_page_preview": True,
            "parse_mode": "Markdown",
        },
    }


def send(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        raise ValueError("telegram token and chat_id are required")
    for chunk in _chunk_text(text):
        payload = build_payload(bot_token, chat_id, chunk)
        try:
            _post_json(payload["url"], payload["json"])
        except Exception as exc:
            # Retry plain text when markdown parsing fails in Telegram.
            if "parse entities" not in str(exc).lower():
                raise
            plain_payload = dict(payload["json"])
            plain_payload.pop("parse_mode", None)
            plain_payload["text"] = chunk
            _post_json(payload["url"], plain_payload)
