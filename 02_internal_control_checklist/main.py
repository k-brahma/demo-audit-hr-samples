"""内部統制チェックリスト管理モジュール。

:description: チェック項目をSQLiteで管理し、進捗率を計算する。
"""

import sqlite3
import csv
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
DB_PATH = DATA_DIR / "checklist.db"

STATUS_OPTIONS = ["未着手", "進行中", "完了", "該当なし"]
PRIORITY_OPTIONS = ["高", "中", "低"]


def init_db() -> None:
    """データベースを初期化し、サンプルデータを投入する。

    :rtype: None
    """
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                item TEXT NOT NULL,
                responsible TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT '未着手',
                comment TEXT DEFAULT ''
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM checklist").fetchone()[0]
        if count == 0:
            _seed_from_csv(conn)


def _seed_from_csv(conn: sqlite3.Connection) -> None:
    sample_csv = DATA_DIR / "checklist.csv"
    if not sample_csv.exists():
        return
    with open(sample_csv, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO checklist (category, item, responsible, priority) VALUES (?,?,?,?)",
                (row["カテゴリ"], row["チェック項目"], row["担当者"], row["優先度"]),
            )


def load_all() -> List[Dict[str, Any]]:
    """全チェック項目を返す。

    :return: チェック項目のリスト
    :rtype: List[Dict[str, Any]]
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM checklist ORDER BY priority DESC, category, id"
        ).fetchall()
    return [dict(r) for r in rows]


def add_item(category: str, item: str, responsible: str, priority: str) -> None:
    """チェック項目を追加する。

    :param category: カテゴリ
    :param item: チェック内容
    :param responsible: 担当者
    :param priority: 優先度
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO checklist (category, item, responsible, priority) VALUES (?,?,?,?)",
            (category, item, responsible, priority),
        )


def update_status(item_id: int, status: str, comment: str = "") -> None:
    """チェック項目のステータスを更新する。

    :param item_id: 項目ID
    :param status: 新しいステータス
    :param comment: コメント
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE checklist SET status=?, comment=? WHERE id=?",
            (status, comment, item_id),
        )


def delete_item(item_id: int) -> None:
    """チェック項目を削除する。

    :param item_id: 項目ID
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM checklist WHERE id=?", (item_id,))


def get_progress() -> Dict[str, Any]:
    """進捗サマリーを返す。

    :return: 総数・完了数・進捗率を含む辞書
    :rtype: Dict[str, Any]
    """
    rows = load_all()
    total = len(rows)
    completed = sum(1 for r in rows if r["status"] in ("完了", "該当なし"))
    rate = (completed / total * 100) if total > 0 else 0.0
    return {"total": total, "completed": completed, "rate": rate}


def export_results() -> Path:
    """チェックリストをCSVへエクスポートする。

    :return: 出力ファイルパス
    :rtype: Path
    """
    import pandas as pd
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "checklist_report.csv"
    rows = load_all()
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
    return out
