"""リスク評価マトリクス生成モジュール。

:description: リスクデータを読み込み、5×5ヒートマップ用データを生成する。
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

LEVEL_LABELS = {1: "非常に低い", 2: "低い", 3: "中程度", 4: "高い", 5: "非常に高い"}


def load_risks(filepath: Path) -> pd.DataFrame:
    """リスクCSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: リスクデータ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df["発生確率"] = pd.to_numeric(df["発生確率"], errors="coerce").fillna(1).clip(1, 5).astype(int)
    df["影響度"] = pd.to_numeric(df["影響度"], errors="coerce").fillna(1).clip(1, 5).astype(int)
    df["リスクスコア"] = df["発生確率"] * df["影響度"]
    return df


def classify_risk_level(score: int) -> str:
    """リスクスコアをレベル文字列に分類する。

    :param score: リスクスコア（1〜25）
    :type score: int
    :return: リスクレベル
    :rtype: str
    """
    if score >= 16:
        return "高"
    if score >= 8:
        return "中"
    return "低"


def build_heatmap_matrix(df: pd.DataFrame) -> np.ndarray:
    """5×5のリスク件数マトリクスを構築する。

    :param df: リスクデータ
    :type df: pd.DataFrame
    :return: 5×5 numpy 配列（行=発生確率、列=影響度）
    :rtype: np.ndarray
    """
    matrix = np.zeros((5, 5), dtype=int)
    for _, row in df.iterrows():
        r = int(row["発生確率"]) - 1
        c = int(row["影響度"]) - 1
        matrix[r][c] += 1
    return matrix


def add_risk(df: pd.DataFrame, category: str, content: str,
             probability: int, impact: int, owner: str) -> pd.DataFrame:
    """リスクを追加する。

    :param df: 既存リスクデータ
    :param category: 分類
    :param content: リスク内容
    :param probability: 発生確率（1〜5）
    :param impact: 影響度（1〜5）
    :param owner: 担当者
    :return: 行追加済み DataFrame
    :rtype: pd.DataFrame
    """
    new_id = f"R{len(df) + 1:03d}"
    new_row = {
        "リスクID": new_id, "分類": category, "リスク内容": content,
        "発生確率": probability, "影響度": impact, "担当者": owner,
        "リスクスコア": probability * impact,
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)


def save_results(df: pd.DataFrame) -> Path:
    """リスクリストをCSVに保存する。

    :param df: リスクデータ
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "risk_report.csv"
    df["リスクレベル"] = df["リスクスコア"].apply(classify_risk_level)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "risks.csv"
