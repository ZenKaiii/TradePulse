from tradepulse.llm.router import call_with_fallback, choose_provider


def test_choose_bailian_when_both_present(monkeypatch):
    monkeypatch.setenv("BAILIAN_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")

    assert choose_provider() == "bailian"


def test_fallback_to_gemini_when_bailian_fails(monkeypatch):
    monkeypatch.setenv("BAILIAN_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")

    def fail_bailian(_prompt: str) -> str:
        raise RuntimeError("bailian down")

    def ok_gemini(_prompt: str) -> str:
        return "gemini-ok"

    assert call_with_fallback("hello", fail_bailian, ok_gemini) == "gemini-ok"
