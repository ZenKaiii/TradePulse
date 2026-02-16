from tradepulse.pipeline.rule_score import score_cluster


def test_score_returns_direction_and_tickers():
    result = score_cluster("NVIDIA raises revenue guidance after AI demand surge", coverage_count=3)

    assert result.direction in {"bullish", "bearish", "neutral"}
    symbols = [t["symbol"] for t in result.affected_tickers]
    assert "NVDA" in symbols
