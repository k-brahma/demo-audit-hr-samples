"""採用コスト可視化モジュール。

:description: 媒体別の採用コスト・CPA（一人当たり採用費）を集計・分析する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"


def load_recruitment(filepath: Path) -> pd.DataFrame:
    """採用コストCSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 採用データ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    for col in ["応募数", "採用数", "費用"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def calculate_cpa(df: pd.DataFrame) -> pd.DataFrame:
    """CPA（一人当たりコスト）と採用率を計算する。

    :param df: 採用データ
    :type df: pd.DataFrame
    :return: CPA・採用率付き DataFrame
    :rtype: pd.DataFrame
    """
    df = df.copy()
    df["CPA"] = df.apply(
        lambda r: r["費用"] / r["採用数"] if r["採用数"] > 0 else float("nan"), axis=1
    )
    df["採用率(%)"] = df.apply(
        lambda r: round(r["採用数"] / r["応募数"] * 100, 1) if r["応募数"] > 0 else 0,
        axis=1,
    )
    df["費用(万円)"] = (df["費用"] / 10000).round(1)
    df["CPA(万円)"] = (df["CPA"] / 10000).round(1)
    return df.sort_values("CPA")


def get_summary(df: pd.DataFrame) -> dict:
    """合計・平均サマリーを返す。

    :param df: CPA計算済みデータ
    :type df: pd.DataFrame
    :return: サマリー辞書
    :rtype: dict
    """
    return {
        "総応募数": int(df["応募数"].sum()),
        "総採用数": int(df["採用数"].sum()),
        "総費用(万円)": round(df["費用"].sum() / 10000, 1),
        "平均CPA(万円)": round(
            df["費用"].sum() / df["採用数"].sum() / 10000, 1
        ) if df["採用数"].sum() > 0 else 0,
        "全体採用率(%)": round(
            df["採用数"].sum() / df["応募数"].sum() * 100, 1
        ) if df["応募数"].sum() > 0 else 0,
    }


def analyze(filepath: Path) -> pd.DataFrame:
    """CSVを読み込みCPA分析済みデータを返す。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 分析結果 DataFrame
    :rtype: pd.DataFrame
    """
    df = load_recruitment(filepath)
    return calculate_cpa(df)


def save_results(df: pd.DataFrame) -> Path:
    """結果をCSVに保存する。

    :param df: 保存する DataFrame
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "recruitment_report.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "recruitment.csv"
