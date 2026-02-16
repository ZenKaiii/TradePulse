from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import re

import yaml


@dataclass
class RuleScoreResult:
    rule_score: float
    direction: str
    affected_tickers: List[Dict[str, str]]


def _load_ticker_aliases() -> Dict[str, Dict[str, List[str]]]:
    root = Path(__file__).resolve().parents[3]
    path = root / "config" / "ticker_aliases.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


_TICKER_ALIASES = _load_ticker_aliases()


def _detect_direction(text: str) -> str:
    bullish_words = ["raises guidance", "beats", "surge", "record revenue", "upgrade"]
    bearish_words = ["cuts guidance", "misses", "probe", "ban", "lawsuit", "downgrade"]

    if any(word in text for word in bullish_words):
        return "bullish"
    if any(word in text for word in bearish_words):
        return "bearish"
    return "neutral"


def _detect_tickers(text: str) -> List[Dict[str, str]]:
    found = []
    lower_text = text.lower()

    def alias_matched(alias: str) -> bool:
        normalized = alias.strip().lower()
        if not normalized:
            return False

        # For alpha-numeric aliases, use token boundaries to avoid substring noise
        # like "MU" accidentally matching "community".
        if re.fullmatch(r"[a-z0-9\.\-\s]+", normalized):
            pattern = rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])"
            return re.search(pattern, lower_text) is not None
        return normalized in lower_text

    for symbol, payload in _TICKER_ALIASES.items():
        aliases = payload.get("aliases", [])
        if any(alias_matched(str(alias)) for alias in aliases):
            found.append({"symbol": symbol, "name": payload.get("name", symbol)})
    return found


def score_cluster(text: str, coverage_count: int) -> RuleScoreResult:
    lower = text.lower()
    direction = _detect_direction(lower)
    tickers = _detect_tickers(lower)

    base = 2.0 + min(max(coverage_count, 0), 5) * 1.2
    direction_bonus = {"bullish": 1.6, "bearish": 1.6, "neutral": 0.4}[direction]
    score = min(10.0, round(base + direction_bonus, 2))

    return RuleScoreResult(rule_score=score, direction=direction, affected_tickers=tickers)
