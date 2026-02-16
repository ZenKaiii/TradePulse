import json
import urllib.error
import urllib.request
from typing import Callable, Dict, Iterable, List


def _post_json(url: str, payload: Dict) -> None:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15):
            return
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        message = body.strip() or str(exc)
        raise RuntimeError(message) from exc


def send_best_effort(senders: Iterable[Callable[[], None]]) -> List[str]:
    errors: List[str] = []
    for sender in senders:
        try:
            sender()
        except (urllib.error.URLError, RuntimeError, ValueError) as exc:
            errors.append(str(exc))
    return errors
