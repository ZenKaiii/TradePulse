from tradepulse.config import LLMConfig
from tradepulse.llm.analyzer import enrich_top_events_with_llm, select_provider


def test_select_provider_prefers_bailian(monkeypatch):
    cfg = LLMConfig(enabled=True, provider="auto")
    monkeypatch.setenv("BAILIAN_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")

    provider = select_provider(cfg)

    assert provider == "bailian"


def test_enrich_top_events_uses_detailed_then_brief(monkeypatch):
    cfg = LLMConfig(enabled=True, provider="auto", detail_top_n=1)
    monkeypatch.setenv("BAILIAN_API_KEY", "x")

    calls = []

    def fake_generate(event, detail_mode, llm_config, provider):
        calls.append(detail_mode)
        return {
            "summary_zh": f"{detail_mode}摘要",
            "impact_reason_zh": f"{detail_mode}原因",
            "direction": "neutral",
            "affected_tickers": [],
            "beginner_note_zh": "这条消息主要影响情绪面",
            "provider": provider,
            "model": llm_config.bailian_model,
        }

    events = [
        {"title": "event-1", "direction": "neutral", "affected_tickers": [], "impact_reason_zh": "x"},
        {"title": "event-2", "direction": "neutral", "affected_tickers": [], "impact_reason_zh": "x"},
    ]

    enriched, meta = enrich_top_events_with_llm(events, cfg, generate_fn=fake_generate)

    assert calls == ["detailed", "brief"]
    assert enriched[0]["summary_zh"] == "detailed摘要"
    assert enriched[1]["summary_zh"] == "brief摘要"
    assert meta["provider"] == "bailian"


def test_enrich_top_events_skips_when_disabled():
    cfg = LLMConfig(enabled=False)
    events = [{"title": "event-1", "direction": "neutral", "affected_tickers": [], "impact_reason_zh": "x"}]

    enriched, meta = enrich_top_events_with_llm(events, cfg)

    assert enriched[0]["impact_reason_zh"] == "x"
    assert meta["provider"] == "rule"
