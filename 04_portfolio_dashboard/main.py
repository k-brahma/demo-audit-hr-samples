"""株式ポートフォリオ損益ダッシュボードモジュール。

:description: 保有株式データを読み込み、損益・資産配分を計算する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"


def load_portfolio(filepath: Path) -> pd.DataFrame:
    """ポートフォリオCSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: ポートフォリオ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    for col in ["保有数", "平均取得単価", "現在価格"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def calculate_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """損益・評価額・配分比率を計算する。

    :param df: ポートフォリオデータ
    :type df: pd.DataFrame
    :return: 損益計算済み DataFrame
    :rtype: pd.DataFrame
    """
    df = df.copy()
    df["取得額"] = df["保有数"] * df["平均取得単価"]
    df["評価額"] = df["保有数"] * df["現在価格"]
    df["損益額"] = df["評価額"] - df["取得額"]
    df["損益率(%)"] = (df["損益額"] / df["取得額"] * 100).round(2)
    total = df["評価額"].sum()
    df["配分(%)"] = (df["評価額"] / total * 100).round(1) if total > 0 else 0
    return df


def get_summary(df: pd.DataFrame) -> dict:
    """ポートフォリオ全体サマリーを返す。

    :param df: 損益計算済みデータ
    :type df: pd.DataFrame
    :return: サマリー辞書
    :rtype: dict
    """
    total_cost = df["取得額"].sum()
    total_eval = df["評価額"].sum()
    total_pnl = df["損益額"].sum()
    rate = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    return {
        "総取得額": total_cost,
        "総評価額": total_eval,
        "総損益額": total_pnl,
        "損益率(%)": round(rate, 2),
    }


def analyze(filepath: Path) -> pd.DataFrame:
    """CSVを読み込み損益計算済みデータを返す。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 分析結果 DataFrame
    :rtype: pd.DataFrame
    """
    df = load_portfolio(filepath)
    return calculate_pnl(df)


def save_results(df: pd.DataFrame) -> Path:
    """結果をCSVに保存する。

    :param df: 保存する DataFrame
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "portfolio_report.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "portfolio.csv"
