from tradepulse.models import CanonicalArticle
from tradepulse.pipeline.cluster import cluster_articles


def test_same_url_articles_cluster_together():
    a = CanonicalArticle(
        id="1",
        title="Fed update",
        url="https://example.com/fed",
        source_name="Reuters",
        published_at="",
    )
    b = CanonicalArticle(
        id="2",
        title="Fed update mirror",
        url="https://example.com/fed",
        source_name="Bloomberg",
        published_at="",
    )

    clusters = cluster_articles([a, b])

    assert len(clusters) == 1
    assert clusters[0].coverage_count == 2
