"""会議コスト計算モジュール。

:description: 参加人数・平均時給・経過時間から会議コストをリアルタイム計算する。
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

PRESETS = [
    {"名前": "朝会（10分）", "人数": 8, "時給": 3500, "分数": 10},
    {"名前": "週次MTG（60分）", "人数": 10, "時給": 4000, "分数": 60},
    {"名前": "経営会議（120分）", "人数": 12, "時給": 8000, "分数": 120},
]


def calculate_cost(participants: int, hourly_rate: int, elapsed_seconds: float) -> float:
    """会議コストを計算する。

    :param participants: 参加人数
    :type participants: int
    :param hourly_rate: 平均時給（円）
    :type hourly_rate: int
    :param elapsed_seconds: 経過秒数
    :type elapsed_seconds: float
    :return: 会議コスト（円）
    :rtype: float
    """
    hours = elapsed_seconds / 3600
    return participants * hourly_rate * hours


def format_cost(cost: float) -> str:
    """コストを日本円フォーマットで返す。

    :param cost: コスト（円）
    :type cost: float
    :return: フォーマット済み文字列
    :rtype: str
    """
    return f"¥{cost:,.0f}"


def format_elapsed(seconds: float) -> str:
    """経過時間を HH:MM:SS 形式で返す。

    :param seconds: 経過秒数
    :type seconds: float
    :return: 時刻文字列
    :rtype: str
    """
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


def save_log(record: dict) -> Path:
    """会議ログを JSON Lines 形式で保存する。

    :param record: 会議記録辞書
    :type record: dict
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "meeting_log.jsonl"
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return out
