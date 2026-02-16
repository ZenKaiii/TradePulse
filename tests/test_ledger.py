from tradepulse.storage.ledger import PushLedger


def test_cluster_pushed_once(tmp_path):
    db = PushLedger(tmp_path / "state.db")

    assert db.should_push("c1") is True
    db.mark_pushed("c1", "run-1")
    assert db.should_push("c1") is False
