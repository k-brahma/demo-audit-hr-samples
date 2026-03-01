"""契約書期限管理モジュール。

:description: 契約書の期限をSQLiteで管理し、残日数・緊急度を計算する。
"""

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
DB_PATH = DATA_DIR / "contracts.db"

CATEGORY_OPTIONS = ["業務委託", "売買", "賃貸借", "保守", "ライセンス", "その他"]

# 残日数の緊急度しきい値
DANGER_DAYS = 30
WARNING_DAYS = 90


def init_db(db_path: Path = DB_PATH) -> None:
    """データベースを初期化し、サンプルデータを投入する。

    :param db_path: データベースファイルパス
    :type db_path: Path
    :rtype: None
    """
    db_path.parent.mkdir(exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                counterparty TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                category TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM contracts").fetchone()[0]
        if count == 0:
            _seed_sample(conn)


def _seed_sample(conn: sqlite3.Connection) -> None:
    today = date.today()
    samples = [
        ("オフィス賃貸借契約", "〇〇不動産", "2022-04-01", "2025-03-31", "賃貸借", "自動更新条項あり"),
        ("基幹システム保守契約", "△△システム", "2024-04-01", "2025-03-31", "保守", ""),
        ("業務委託契約（デザイン）", "□□デザイン事務所", "2024-10-01", "2025-09-30", "業務委託", ""),
        ("クラウドサービス利用契約", "○○クラウド", "2023-07-01", "2026-06-30", "ライセンス", "年次更新"),
        ("物品売買基本契約", "▲▲商事", "2024-01-01", "2026-12-31", "売買", ""),
        ("清掃業務委託契約", "××メンテナンス", "2024-04-01", "2025-04-30", "業務委託", "更新要確認"),
    ]
    conn.executemany(
        "INSERT INTO contracts (name, counterparty, start_date, end_date, category, notes) VALUES (?,?,?,?,?,?)",
        samples,
    )


def load_all(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """全契約を残日数付きで返す。

    :param db_path: データベースファイルパス
    :type db_path: Path
    :return: 契約情報リスト
    :rtype: List[Dict[str, Any]]
    """
    today = date.today()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM contracts ORDER BY end_date").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        end = datetime.strptime(d["end_date"], "%Y-%m-%d").date()
        d["残日数"] = (end - today).days
        d["緊急度"] = _urgency(d["残日数"])
        result.append(d)
    return result


def _urgency(days: int) -> str:
    if days < 0:
        return "期限切れ"
    if days <= DANGER_DAYS:
        return "危険"
    if days <= WARNING_DAYS:
        return "警告"
    return "正常"


def add_contract(name: str, counterparty: str, start_date: str,
                 end_date: str, category: str, notes: str = "",
                 db_path: Path = DB_PATH) -> None:
    """契約を追加する。

    :param name: 契約名
    :param counterparty: 相手先
    :param start_date: 開始日（YYYY-MM-DD）
    :param end_date: 終了日（YYYY-MM-DD）
    :param category: カテゴリ
    :param notes: 備考
    :param db_path: データベースファイルパス
    :type db_path: Path
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO contracts (name, counterparty, start_date, end_date, category, notes) VALUES (?,?,?,?,?,?)",
            (name, counterparty, start_date, end_date, category, notes),
        )


def delete_contract(contract_id: int, db_path: Path = DB_PATH) -> None:
    """契約を削除する。

    :param contract_id: 契約ID
    :type contract_id: int
    :param db_path: データベースファイルパス
    :type db_path: Path
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM contracts WHERE id=?", (contract_id,))


def export_results(db_path: Path = DB_PATH) -> Path:
    """契約リストをCSVへエクスポートする。

    :param db_path: データベースファイルパス
    :type db_path: Path
    :return: 出力ファイルパス
    :rtype: Path
    """
    import pandas as pd
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "contracts_report.csv"
    pd.DataFrame(load_all(db_path)).to_csv(out, index=False, encoding="utf-8-sig")
    return out
