"""勤怠データ異常検知モジュール。

:description: 勤怠CSVを読み込み月次残業時間を集計し、36協定違反リスクを検出する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

OVERTIME_WARNING = 45.0  # 警告ライン（時間/月）
OVERTIME_DANGER = 80.0   # 危険ライン（時間/月）

STATUS_COLORS = {
    "正常": "#d4edda",
    "警告": "#fff3cd",
    "危険": "#f8d7da",
}


def load_attendance(filepath: Path) -> pd.DataFrame:
    """勤怠CSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 勤怠データ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df["日付"] = pd.to_datetime(df["日付"])
    df["残業時間"] = pd.to_numeric(df["残業時間"], errors="coerce").fillna(0.0)
    return df


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """日次データを月次集計する。

    :param df: 日次勤怠データ
    :type df: pd.DataFrame
    :return: 月次集計 DataFrame
    :rtype: pd.DataFrame
    """
    df = df.copy()
    df["年月"] = df["日付"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby(["社員ID", "氏名", "部署", "年月"])["残業時間"]
        .sum()
        .reset_index()
        .rename(columns={"残業時間": "月次残業時間"})
    )
    return monthly.sort_values("月次残業時間", ascending=False).reset_index(drop=True)


def classify_status(hours: float) -> str:
    """残業時間をステータス文字列に分類する。

    :param hours: 月次残業時間
    :type hours: float
    :return: ステータス文字列
    :rtype: str
    """
    if hours >= OVERTIME_DANGER:
        return "危険"
    if hours >= OVERTIME_WARNING:
        return "警告"
    return "正常"


def analyze(filepath: Path) -> pd.DataFrame:
    """CSVを読み込みステータス付き月次集計を返す。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 分析結果 DataFrame
    :rtype: pd.DataFrame
    """
    df = load_attendance(filepath)
    monthly = aggregate_monthly(df)
    monthly["ステータス"] = monthly["月次残業時間"].apply(classify_status)
    return monthly


def save_results(df: pd.DataFrame) -> Path:
    """結果をCSVに保存する。

    :param df: 保存する DataFrame
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "anomaly_report.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "attendance.csv"
