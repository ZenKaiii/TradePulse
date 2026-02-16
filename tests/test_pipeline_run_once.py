from tradepulse.pipeline.run_once import run_once


def test_run_once_returns_digest_and_stats():
    result = run_once(dry_run=True)
    assert "digest" in result
    assert "stats" in result
