# 転職活動用 Pythonデモアプリ集

監査・人事経験 × Python スキルをアピールするための Tkinter デスクトップアプリ 10本。

---

## 環境セットアップ

```powershell
# 仮想環境の作成（初回のみ）
python -m venv .venv

# 仮想環境の有効化
.venv\Scripts\Activate.ps1

# 依存ライブラリのインストール
pip install -r requirements.txt
```

---

## 起動方法

各アプリのディレクトリに移動して `gui.py` を実行する。

```powershell
cd 01_attendance_anomaly
python gui.py
```

---

## アプリ一覧

### 01 勤怠データ異常検知ツール
**キーワード：** 人事 × 36協定 × データ分析

| 項目 | 内容 |
|------|------|
| 起動 | `cd 01_attendance_anomaly` → `python gui.py` |
| サンプルデータ | `data/attendance.csv` |
| 出力 | `results/anomaly_report.csv` |
| チャート | 横棒グラフ（残業時間・ステータス色分け） |

CSVを読み込み、月次残業時間を集計。45時間超を「警告」、80時間超を「危険」として色分け表示する。

---

### 02 内部統制チェックリスト
**キーワード：** 監査 × 業務効率化 × SQLite

| 項目 | 内容 |
|------|------|
| 起動 | `cd 02_internal_control_checklist` → `python gui.py` |
| データ | `data/checklist.db`（初回自動生成） |
| 出力 | `results/checklist_report.csv` |
| チャート | 進捗バー |

チェック項目をSQLiteで管理。ステータス更新・追加・削除・進捗率表示に対応。

---

### 03 採用コスト可視化ツール
**キーワード：** 人事 × CPA × 媒体比較

| 項目 | 内容 |
|------|------|
| 起動 | `cd 03_recruitment_cost` → `python gui.py` |
| サンプルデータ | `data/recruitment.csv` |
| 出力 | `results/recruitment_report.csv` |
| チャート | 棒グラフ（媒体別CPA比較） |

媒体別の応募数・採用数・費用から一人当たり採用コスト（CPA）を自動計算。最安値媒体をハイライト表示。

---

### 04 株式ポートフォリオ 損益ダッシュボード
**キーワード：** 金融 × 損益計算 × 資産配分

| 項目 | 内容 |
|------|------|
| 起動 | `cd 04_portfolio_dashboard` → `python gui.py` |
| サンプルデータ | `data/portfolio.csv` |
| 出力 | `results/portfolio_report.csv` |
| チャート | 円グラフ（資産配分） |

保有株・平均取得単価・現在価格から損益額・損益率・資産配分を一覧表示。

---

### 05 給与バンド分析ツール
**キーワード：** 人事 × 統計 × 報酬設計

| 項目 | 内容 |
|------|------|
| 起動 | `cd 05_salary_band_analysis` → `python gui.py` |
| サンプルデータ | `data/salary.csv` |
| 出力 | `results/salary_stats.csv` |
| チャート | ボックスプロット（等級別・部署別切り替え） |

等級・部署ごとの給与分布を箱ひげ図で可視化。最小・最大・平均・中央値の統計テーブルも表示。

---

### 06 リスク評価マトリクス自動生成ツール
**キーワード：** 監査 × リスク管理 × ヒートマップ

| 項目 | 内容 |
|------|------|
| 起動 | `cd 06_risk_matrix` → `python gui.py` |
| サンプルデータ | `data/risks.csv` |
| 出力 | `results/risk_report.csv` / `results/risk_matrix.png` |
| チャート | 5×5 ヒートマップ |

発生確率×影響度のマトリクスをヒートマップで自動描画。リスクの追加入力にも対応。PNG出力可能。

---

### 07 会議コスト計算機
**キーワード：** 管理部門 × 意識改革 × リアルタイムUI

| 項目 | 内容 |
|------|------|
| 起動 | `cd 07_meeting_cost_calculator` → `python gui.py` |
| データ不要 | ─ |
| 出力 | `results/meeting_log.jsonl` |
| 特徴 | リアルタイムタイマー＆コストカウントアップ |

参加人数・平均時給を設定してタイマーをスタートすると、会議コストが毎秒リアルタイム更新される。
コスト増加に応じて表示色が変化。プリセット3種付き。

> **面接デモ向けポイント：** 動く画面が一番インパクトが出るアプリ。

---

### 08 契約書 期限管理ツール
**キーワード：** 総務・法務 × 期限管理 × SQLite

| 項目 | 内容 |
|------|------|
| 起動 | `cd 08_contract_deadline_manager` → `python gui.py` |
| データ | `data/contracts.db`（初回自動生成） |
| 出力 | `results/contracts_report.csv` |
| チャート | 残日数による行の色分け |

契約書の終了日を管理し、残り日数で「正常（緑）」「警告（黄）」「危険/期限切れ（赤）」に色分け。追加・削除に対応。

---

### 09 KPI トラッカー
**キーワード：** 経営管理 × 達成率 × 折れ線グラフ

| 項目 | 内容 |
|------|------|
| 起動 | `cd 09_kpi_tracker` → `python gui.py` |
| サンプルデータ | `data/kpi.csv` |
| 出力 | `results/kpi_report.csv` |
| チャート | 折れ線グラフ（目標 vs 実績・達成率付き） |

KPI名を選択すると月次推移を折れ線グラフで表示。達成率90%未満を「警告」、70%未満を「危険」として色分け。

---

### 10 従業員サーベイ結果 集計・分析ツール
**キーワード：** 人事 × エンゲージメント × レーダーチャート

| 項目 | 内容 |
|------|------|
| 起動 | `cd 10_employee_survey` → `python gui.py` |
| サンプルデータ | `data/survey.csv` |
| 出力 | `results/survey_report.csv` |
| チャート | 棒グラフ（設問別）／レーダーチャート（部署別比較） |

従業員サーベイのCSVを読み込み、設問別平均スコアと部署別比較を可視化。表示モードを切り替えてレーダーチャートでも確認できる。

---

## ディレクトリ構造

```
job-hunting-preparation/
├── README.md
├── requirements.txt
├── 01_attendance_anomaly/
│   ├── main.py        # ビジネスロジック（分析・計算）
│   ├── gui.py         # Tkinter GUI（起動エントリポイント）
│   ├── data/          # サンプルデータ（CSV / SQLite）
│   └── results/       # 出力ファイル保存先
├── 02_internal_control_checklist/
│   └── ...（以下同様）
...
```

---

## 依存ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| `pandas` | データ読み込み・集計・CSV出力 |
| `matplotlib` | グラフ描画（棒・折れ線・円・箱ひげ図・ヒートマップ・レーダー） |
| `tkinter` | GUI（Python標準ライブラリ） |
| `sqlite3` | DB永続化（Python標準ライブラリ） |

---

## 面接でのアピールポイント

- **業務課題を自分で特定してコード化した** という経験として語れる
- 各アプリに「なぜ作ったか」のストーリーが紐づいている（監査・人事の実務知識）
- `main.py`（ロジック）と `gui.py`（UI）を分離した設計になっており、可読性・保守性を意識したことを示せる
- `data/` → 分析 → `results/` というデータフローが明確
