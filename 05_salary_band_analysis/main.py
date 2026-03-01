"""給与バンド分析モジュール。

:description: 従業員給与データを読み込み、等級・部署別の統計分析を行う。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"


def load_salary(filepath: Path) -> pd.DataFrame:
    """給与CSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: 給与データ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df["年収"] = pd.to_numeric(df["年収"], errors="coerce").fillna(0)
    df["年収(万円)"] = (df["年収"] / 10000).round(0).astype(int)
    df["等級"] = df["等級"].astype(str)
    return df


def get_grade_stats(df: pd.DataFrame) -> pd.DataFrame:
    """等級別の統計量を返す。

    :param df: 給与データ
    :type df: pd.DataFrame
    :return: 等級別統計 DataFrame
    :rtype: pd.DataFrame
    """
    stats = (
        df.groupby("等級")["年収(万円)"]
        .agg(["min", "max", "mean", "median", "count"])
        .reset_index()
    )
    stats.columns = ["等級", "最小値", "最大値", "平均値", "中央値", "人数"]
    stats["平均値"] = stats["平均値"].round(0).astype(int)
    stats["中央値"] = stats["中央値"].round(0).astype(int)
    return stats.sort_values("等級")


def get_dept_stats(df: pd.DataFrame) -> pd.DataFrame:
    """部署別の統計量を返す。

    :param df: 給与データ
    :type df: pd.DataFrame
    :return: 部署別統計 DataFrame
    :rtype: pd.DataFrame
    """
    stats = (
        df.groupby("部署")["年収(万円)"]
        .agg(["min", "max", "mean", "median", "count"])
        .reset_index()
    )
    stats.columns = ["部署", "最小値", "最大値", "平均値", "中央値", "人数"]
    stats["平均値"] = stats["平均値"].round(0).astype(int)
    stats["中央値"] = stats["中央値"].round(0).astype(int)
    return stats


def get_boxplot_data(df: pd.DataFrame, group_col: str) -> dict:
    """ボックスプロット用のグループ別データを返す。

    :param df: 給与データ
    :param group_col: グルーピング列名（等級 or 部署）
    :type df: pd.DataFrame
    :type group_col: str
    :return: グループ名をキー、年収リストを値とする辞書
    :rtype: dict
    """
    return {
        str(grp): list(sub["年収(万円)"])
        for grp, sub in df.groupby(group_col)
    }


def save_results(df: pd.DataFrame) -> Path:
    """統計結果をCSVに保存する。

    :param df: 保存する DataFrame
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "salary_stats.csv"
    get_grade_stats(df).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "salary.csv"
