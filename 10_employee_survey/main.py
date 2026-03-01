"""従業員サーベイ結果集計・分析モジュール。

:description: サーベイCSVを読み込み、設問別・部署別の平均スコアを集計する。
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

QUESTION_LABELS = {
    "Q1_業務満足度": "業務満足度",
    "Q2_職場環境": "職場環境",
    "Q3_上司との関係": "上司との関係",
    "Q4_給与待遇": "給与待遇",
    "Q5_成長機会": "成長機会",
    "Q6_会社への信頼": "会社への信頼",
    "Q7_ワークライフバランス": "WLB",
    "Q8_チームワーク": "チームワーク",
}

QUESTION_COLS = list(QUESTION_LABELS.keys())


def load_survey(filepath: Path) -> pd.DataFrame:
    """サーベイCSVを読み込む。

    :param filepath: CSVファイルパス
    :type filepath: Path
    :return: サーベイデータ DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    for col in QUESTION_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def aggregate_by_question(df: pd.DataFrame) -> pd.DataFrame:
    """設問別の平均スコアを返す。

    :param df: サーベイデータ
    :type df: pd.DataFrame
    :return: 設問別平均 DataFrame
    :rtype: pd.DataFrame
    """
    means = df[QUESTION_COLS].mean().round(2)
    result = pd.DataFrame({
        "設問コード": means.index,
        "設問名": [QUESTION_LABELS[q] for q in means.index],
        "平均スコア": means.values,
    })
    return result.sort_values("平均スコア", ascending=False).reset_index(drop=True)


def aggregate_by_department(df: pd.DataFrame) -> pd.DataFrame:
    """部署別の設問平均スコアを返す。

    :param df: サーベイデータ
    :type df: pd.DataFrame
    :return: 部署×設問の平均スコア DataFrame
    :rtype: pd.DataFrame
    """
    dept_means = df.groupby("部署")[QUESTION_COLS].mean().round(2)
    dept_means.columns = [QUESTION_LABELS[c] for c in dept_means.columns]
    dept_means["総合平均"] = dept_means.mean(axis=1).round(2)
    return dept_means.reset_index()


def get_overall_score(df: pd.DataFrame) -> float:
    """全設問・全員の総合平均スコアを返す。

    :param df: サーベイデータ
    :type df: pd.DataFrame
    :return: 総合平均スコア
    :rtype: float
    """
    return round(df[QUESTION_COLS].values.mean(), 2)


def get_departments(df: pd.DataFrame) -> list:
    """部署一覧を返す。

    :param df: サーベイデータ
    :type df: pd.DataFrame
    :return: 部署名リスト
    :rtype: list
    """
    return sorted(df["部署"].unique().tolist())


def save_results(df: pd.DataFrame) -> Path:
    """集計結果をCSVに保存する。

    :param df: サーベイデータ
    :type df: pd.DataFrame
    :return: 保存先パス
    :rtype: Path
    """
    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / "survey_report.csv"
    aggregate_by_department(df).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def default_data_path() -> Path:
    """デフォルトのサンプルデータパスを返す。

    :return: サンプルCSVパス
    :rtype: Path
    """
    return DATA_DIR / "survey.csv"
