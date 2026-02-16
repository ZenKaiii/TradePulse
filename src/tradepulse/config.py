from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class DigestConfig:
    top_n: int = 10


@dataclass
class SourcesConfig:
    profile: str = "trader"


@dataclass
class WatchlistsConfig:
    stocks: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    geopolitics: List[str] = field(default_factory=list)


@dataclass
class DeliveryConfig:
    channels: List[str] = field(default_factory=lambda: ["dingtalk"])


@dataclass
class UserConfig:
    digest: DigestConfig = field(default_factory=DigestConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    watchlists: WatchlistsConfig = field(default_factory=WatchlistsConfig)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def load_user_config(path: Path) -> UserConfig:
    raw = {}
    if path.exists():
        raw = _as_dict(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

    digest_raw = _as_dict(raw.get("digest"))
    sources_raw = _as_dict(raw.get("sources"))
    watch_raw = _as_dict(raw.get("watchlists"))
    delivery_raw = _as_dict(raw.get("delivery"))

    top_n = int(digest_raw.get("top_n", 10))
    top_n = max(1, min(top_n, 50))

    channels = _as_list(delivery_raw.get("channels")) or ["dingtalk"]

    return UserConfig(
        digest=DigestConfig(top_n=top_n),
        sources=SourcesConfig(profile=str(sources_raw.get("profile", "trader"))),
        watchlists=WatchlistsConfig(
            stocks=_as_list(watch_raw.get("stocks")),
            keywords=_as_list(watch_raw.get("keywords")),
            geopolitics=_as_list(watch_raw.get("geopolitics")),
        ),
        delivery=DeliveryConfig(channels=channels),
    )
