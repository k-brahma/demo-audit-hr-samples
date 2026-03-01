"""KPIトラッカーモジュール。

:description: KPI目標・実績データを読み込み、達成率と推移を分析する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

ACHIEVEMENT_WARNING = 90.0   # 達成率 90% 未満は警告
ACHIEVEMENT_DANGER = 70.0    # 達成率 70% 未満は危険


def load_kpi(filepath: Path) -> pd.DataFrame:
    """KPI CSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: KPIデータ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df["目標"] = pd.to_numeric(df["目標"], errors="coerce").fillna(0)
    df["実績"] = pd.to_numeric(df["実績"], errors="coerce").fillna(0)
    return df


def calculate_achievement(df: pd.DataFrame) -> pd.DataFrame:
    """達成率とステータスを計算する。

    :param df: KPIデータ
    :type df: pd.DataFrame
    :return: 達成率・ステータス付き DataFrame
    :rtype: pd.DataFrame
    """
    df = df.copy()
    df["達成率(%)"] = df.apply(
        lambda r: round(r["実績"] / r["目標"] * 100, 1) if r["目標"] > 0 else 0,
        axis=1,
    )
    df["ステータス"] = df["達成率(%)"].apply(_classify)
    return df


def _classify(rate: float) -> str:
    if rate < ACHIEVEMENT_DANGER:
        return "危険"
    if rate < ACHIEVEMENT_WARNING:
        return "警告"
    return "達成"


def get_kpi_names(df: pd.DataFrame) -> list:
    """KPI名の一覧を返す。

    :param df: KPIデータ
    :type df: pd.DataFrame
    :return: KPI名リスト
    :rtype: list
    """
    return sorted(df["KPI名"].unique().tolist())


def get_kpi_trend(df: pd.DataFrame, kpi_name: str) -> pd.DataFrame:
    """指定KPIの時系列データを返す。

    :param df: 達成率計算済みデータ
    :param kpi_name: KPI名
    :type df: pd.DataFrame
    :type kpi_name: str
    :return: 該当KPIの時系列 DataFrame
    :rtype: pd.DataFrame
    """
    return df[df["KPI名"] == kpi_name].sort_values("年月").reset_index(drop=True)


def get_latest_summary(df: pd.DataFrame) -> pd.DataFrame:
    """最新月の全KPIサマリーを返す。

    :param df: 達成率計算済みデータ
    :type df: pd.DataFrame
    :return: 最新月サマリー DataFrame
    :rtype: pd.DataFrame
    """
    latest_month = df["年月"].max()
    return df[df["年月"] == latest_month].reset_index(drop=True)


def save_results(df: pd.DataFrame) -> Path:
    """結果をCSVに保存する。達成率列がない場合は自動計算して付与する。

    :param df: 保存する DataFrame（生データまたは達成率計算済みデータ）
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "kpi_report.csv"
    if "達成率(%)" not in df.columns:
        df = calculate_achievement(df)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "kpi.csv"
