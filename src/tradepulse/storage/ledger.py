import sqlite3
from pathlib import Path


class PushLedger:
    def __init__(self, path: Path):
        self._conn = sqlite3.connect(str(path))
        self._conn.execute(
            "create table if not exists pushed("
            "cluster_id text primary key, "
            "run_id text not null, "
            "pushed_at text not null)"
        )
        self._conn.commit()

    def should_push(self, cluster_id: str) -> bool:
        row = self._conn.execute(
            "select 1 from pushed where cluster_id = ?", (cluster_id,)
        ).fetchone()
        return row is None

    def mark_pushed(self, cluster_id: str, run_id: str) -> None:
        self._conn.execute(
            "insert or ignore into pushed(cluster_id, run_id, pushed_at) "
            "values(?, ?, datetime('now'))",
            (cluster_id, run_id),
        )
        self._conn.commit()
