# 01 勤怠データ異常検知ツール

## 概要

社員ごとの日次勤怠データ（CSV）を読み込み、月次残業時間を集計して36協定違反リスクを自動検出するツール。

- 残業 **45時間超** → 🟡 警告
- 残業 **80時間超** → 🔴 危険（過労死ライン）

## 起動

```powershell
cd 01_attendance_anomaly
python gui.py
```

## 使い方

1. 「CSVを開く」ボタンで `data/attendance.csv` を選択
2. 左側のテーブルに社員ごとの月次残業時間と色分けステータスが表示される
3. 右側の横棒グラフで一目で状況を把握できる
4. 「結果を保存」で `results/anomaly_report.csv` に出力

## ファイル構成

```
01_attendance_anomaly/
├── main.py          # CSVロード・月次集計・ステータス分類ロジック
├── gui.py           # Tkinter GUI（Treeview + matplotlib 横棒グラフ）
├── data/
│   └── attendance.csv   # サンプル勤怠データ（5名・1ヶ月分）
└── results/
    └── anomaly_report.csv   # 出力レポート
```

## サンプルデータ仕様

| 列名 | 内容 |
|------|------|
| 社員ID | 従業員識別子（例: E001） |
| 氏名 | 氏名 |
| 部署 | 所属部署名 |
| 日付 | YYYY-MM-DD 形式 |
| 残業時間 | その日の残業時間（時間単位） |

## 主要ロジック（main.py）

| 関数 | 内容 |
|------|------|
| `load_attendance(filepath)` | CSVを読み込みデータ型を整える |
| `aggregate_monthly(df)` | 日次→月次に集計 |
| `classify_status(hours)` | 時間数をステータス文字列に変換 |
| `analyze(filepath)` | 上記を統合して結果DataFrameを返す |
| `save_results(df)` | `results/` にCSV保存 |

## 特徴・ポイント

- **業務知識の直接応用：** 36協定の警告ラインを知っているからこそ設定できる閾値
- **Excelでやっていた作業の自動化** という文脈で説明できる
- `pandas` の `groupby` + `sort_values` によるデータ集計を示せる
- 「危険度に応じた色分け」というUX配慮を説明できる
