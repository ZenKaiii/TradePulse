from pathlib import Path


def test_hourly_workflow_exists():
    assert Path(".github/workflows/hourly.yml").exists()
