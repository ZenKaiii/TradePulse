from dataclasses import dataclass
from typing import Dict, List

from tradepulse.models import CanonicalArticle


@dataclass
class EventCluster:
    cluster_id: str
    articles: List[CanonicalArticle]
    coverage_count: int


def cluster_articles(items: List[CanonicalArticle]) -> List[EventCluster]:
    buckets: Dict[str, List[CanonicalArticle]] = {}

    for item in items:
        key = item.url or item.id
        buckets.setdefault(key, []).append(item)

    return [
        EventCluster(cluster_id=cluster_id, articles=articles, coverage_count=len(articles))
        for cluster_id, articles in buckets.items()
    ]
