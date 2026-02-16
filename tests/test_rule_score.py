from tradepulse.pipeline.rule_score import score_cluster


def test_short_ticker_does_not_match_substring_noise():
    result = score_cluster(
        "The Munich conference ended the post-war order",
        coverage_count=1,
    )
    symbols = {item["symbol"] for item in result.affected_tickers}
    assert "MU" not in symbols


def test_short_ticker_matches_as_token():
    result = score_cluster(
        "MU rises after memory pricing improved",
        coverage_count=1,
    )
    symbols = {item["symbol"] for item in result.affected_tickers}
    assert "MU" in symbols
