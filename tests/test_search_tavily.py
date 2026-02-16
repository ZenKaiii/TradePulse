from tradepulse.config import SearchEnhanceConfig
from tradepulse.search.tavily import enrich_events_with_tavily


def test_tavily_enrichment_applies_to_top_n(monkeypatch):
    events = [
        {"title": "NVIDIA raises guidance", "analysis_level": "detailed"},
        {"title": "Fed rate decision outlook", "analysis_level": "detailed"},
    ]

    class FakeResponse:
        def raise_for_status(self):
            return

        def json(self):
            return {
                "answer": "AI demand remains strong across hyperscalers.",
                "results": [{"title": "AI demand news", "url": "https://example.com/ai"}],
            }

    monkeypatch.setattr("tradepulse.search.tavily.httpx.post", lambda *args, **kwargs: FakeResponse())
    cfg = SearchEnhanceConfig(enabled=True, top_n=1, max_results=3, timeout_sec=8.0)
    enriched, meta = enrich_events_with_tavily(events, cfg, {"TAVILY_API_KEY": "tvly-xxx"})

    assert "search_context" in enriched[0]
    assert "search_context" not in enriched[1]
    assert meta["provider"] == "tavily"
    assert meta["hits"] == 1


def test_tavily_enrichment_skips_when_disabled():
    events = [{"title": "NVIDIA raises guidance", "analysis_level": "detailed"}]
    cfg = SearchEnhanceConfig(enabled=False)
    enriched, meta = enrich_events_with_tavily(events, cfg, {"TAVILY_API_KEY": "tvly-xxx"})

    assert enriched == events
    assert meta["provider"] == "none"
