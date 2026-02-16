from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import yaml


@dataclass
class DigestConfig:
    top_n: int = 10


@dataclass
class SourcesConfig:
    profile: str = "trader"
    tier: str = "core"
    min_health_score: int = 30


@dataclass
class WatchlistsConfig:
    stocks: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    geopolitics: List[str] = field(default_factory=list)


@dataclass
class DeliveryConfig:
    channels: List[str] = field(default_factory=lambda: ["dingtalk"])


@dataclass
class MarketRegimeConfig:
    enabled: bool = True
    us_enabled: bool = True
    a_share_enabled: bool = True
    us_top_n: int = 3
    a_share_top_n: int = 5
    request_timeout_sec: float = 8.0


@dataclass
class UserConfig:
    digest: DigestConfig = field(default_factory=DigestConfig)
    sources: SourcesConfig = field(default_factory=SourcesConfig)
    watchlists: WatchlistsConfig = field(default_factory=WatchlistsConfig)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)
    market_regime: MarketRegimeConfig = field(default_factory=MarketRegimeConfig)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def _coerce_int(
    value: Optional[str],
    default: int,
    min_value: int,
    max_value: int,
) -> int:
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(parsed, max_value))


def _coerce_float(
    value: Optional[str],
    default: float,
    min_value: float,
    max_value: float,
) -> float:
    if value is None or value == "":
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(parsed, max_value))


def _coerce_bool(value: Optional[str], default: bool) -> bool:
    if value is None or value == "":
        return default

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return _coerce_bool(value, default)
    return default


def _coerce_csv(value: Optional[str], default: List[str]) -> List[str]:
    if not value:
        return default

    items = []
    normalized = value.replace("\n", ",")
    for part in normalized.split(","):
        item = part.strip()
        if item:
            items.append(item)
    return items or default


def load_user_config(path: Path) -> UserConfig:
    raw = {}
    if path.exists():
        raw = _as_dict(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

    digest_raw = _as_dict(raw.get("digest"))
    sources_raw = _as_dict(raw.get("sources"))
    watch_raw = _as_dict(raw.get("watchlists"))
    delivery_raw = _as_dict(raw.get("delivery"))
    market_raw = _as_dict(raw.get("market_regime"))

    top_n = int(digest_raw.get("top_n", 10))
    top_n = max(1, min(top_n, 50))

    channels = _as_list(delivery_raw.get("channels")) or ["dingtalk"]

    return UserConfig(
        digest=DigestConfig(top_n=top_n),
        sources=SourcesConfig(
            profile=str(sources_raw.get("profile", "trader")),
            tier=str(sources_raw.get("tier", "core")),
            min_health_score=max(0, min(int(sources_raw.get("min_health_score", 30)), 100)),
        ),
        watchlists=WatchlistsConfig(
            stocks=_as_list(watch_raw.get("stocks")),
            keywords=_as_list(watch_raw.get("keywords")),
            geopolitics=_as_list(watch_raw.get("geopolitics")),
        ),
        delivery=DeliveryConfig(channels=channels),
        market_regime=MarketRegimeConfig(
            enabled=_as_bool(market_raw.get("enabled"), True),
            us_enabled=_as_bool(market_raw.get("us_enabled"), True),
            a_share_enabled=_as_bool(market_raw.get("a_share_enabled"), True),
            us_top_n=max(1, min(int(market_raw.get("us_top_n", 3)), 10)),
            a_share_top_n=max(1, min(int(market_raw.get("a_share_top_n", 5)), 20)),
            request_timeout_sec=max(
                1.0,
                min(float(market_raw.get("request_timeout_sec", 8.0)), 30.0),
            ),
        ),
    )


def apply_env_overrides(
    config: UserConfig,
    environ: Optional[Mapping[str, str]] = None,
) -> UserConfig:
    env = dict(environ or {})
    return UserConfig(
        digest=DigestConfig(
            top_n=_coerce_int(env.get("TRADEPULSE_TOP_N"), config.digest.top_n, 1, 50),
        ),
        sources=SourcesConfig(
            profile=env.get("TRADEPULSE_SOURCE_PROFILE", config.sources.profile),
            tier=env.get("TRADEPULSE_SOURCE_TIER", config.sources.tier),
            min_health_score=_coerce_int(
                env.get("TRADEPULSE_MIN_HEALTH_SCORE"),
                config.sources.min_health_score,
                0,
                100,
            ),
        ),
        watchlists=WatchlistsConfig(
            stocks=_coerce_csv(env.get("TRADEPULSE_STOCKS"), config.watchlists.stocks),
            keywords=_coerce_csv(
                env.get("TRADEPULSE_KEYWORDS"),
                config.watchlists.keywords,
            ),
            geopolitics=_coerce_csv(
                env.get("TRADEPULSE_GEOPOLITICS"),
                config.watchlists.geopolitics,
            ),
        ),
        delivery=DeliveryConfig(
            channels=[
                item.lower()
                for item in _coerce_csv(
                    env.get("TRADEPULSE_CHANNELS"),
                    config.delivery.channels,
                )
            ],
        ),
        market_regime=MarketRegimeConfig(
            enabled=_coerce_bool(
                env.get("TRADEPULSE_MARKET_ENABLED"),
                config.market_regime.enabled,
            ),
            us_enabled=_coerce_bool(
                env.get("TRADEPULSE_MARKET_US_ENABLED"),
                config.market_regime.us_enabled,
            ),
            a_share_enabled=_coerce_bool(
                env.get("TRADEPULSE_MARKET_A_SHARE_ENABLED"),
                config.market_regime.a_share_enabled,
            ),
            us_top_n=_coerce_int(
                env.get("TRADEPULSE_MARKET_US_TOP_N"),
                config.market_regime.us_top_n,
                1,
                10,
            ),
            a_share_top_n=_coerce_int(
                env.get("TRADEPULSE_MARKET_A_SHARE_TOP_N"),
                config.market_regime.a_share_top_n,
                1,
                20,
            ),
            request_timeout_sec=_coerce_float(
                env.get("TRADEPULSE_MARKET_TIMEOUT_SEC"),
                config.market_regime.request_timeout_sec,
                1.0,
                30.0,
            ),
        ),
    )
