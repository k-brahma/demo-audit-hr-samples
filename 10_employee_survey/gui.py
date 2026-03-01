"""従業員サーベイ結果集計・分析 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"

VIEW_OPTIONS = ["設問別（全体）", "部署別比較（レーダー）"]


class SurveyApp(tk.Tk):
    """従業員サーベイ集計メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("従業員サーベイ 結果集計・分析")
        self.geometry("1080x700")
        self._df = None
        self._sort_col = ""
        self._sort_reverse = False
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)

        ttk.Label(toolbar, text="表示モード:").pack(side=tk.LEFT, padx=(16, 4))
        self._view_var = tk.StringVar(value=VIEW_OPTIONS[0])
        cb = ttk.Combobox(toolbar, textvariable=self._view_var,
                          values=VIEW_OPTIONS, width=22, state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_chart())

        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=8)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # 総合スコア表示
        score_frame = ttk.LabelFrame(self, text="総合評価", padding=6)
        score_frame.pack(fill=tk.X, padx=8, pady=2)
        self._overall_var = tk.StringVar(value="—")
        self._respondents_var = tk.StringVar(value="回答数: —")
        ttk.Label(score_frame, text="総合平均スコア（5点満点）", font=("Yu Gothic", 9)).pack(side=tk.LEFT)
        ttk.Label(score_frame, textvariable=self._overall_var,
                  font=("Yu Gothic", 18, "bold"), foreground="#2980b9").pack(side=tk.LEFT, padx=12)
        ttk.Label(score_frame, textvariable=self._respondents_var,
                  foreground="gray").pack(side=tk.LEFT, padx=8)

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: 設問別平均テーブル
        left = ttk.LabelFrame(pane, text="設問別 平均スコア", padding=4)
        pane.add(left, weight=1)

        cols = ("設問名", "平均スコア")
        self._cols = cols
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for col in cols:
            self._tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
        self._tree.column("設問名", width=160, anchor=tk.W)
        self._tree.column("平均スコア", width=90, anchor=tk.CENTER)
        self._tree.tag_configure("high", background="#d4edda")
        self._tree.tag_configure("low", background="#f8d7da")

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: グラフ
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._fig, self._ax = plt.subplots(figsize=(6, 5))
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_empty_chart()

    def _sort_by(self, col: str) -> None:
        """カラムヘッダークリックで並べ替え。

        :param col: ソート対象カラム名
        :type col: str
        """
        self._sort_reverse = (self._sort_col == col) and not self._sort_reverse
        self._sort_col = col
        self._apply_sort()

    def _apply_sort(self) -> None:
        """現在のソート状態をツリーに適用する。"""
        col = self._sort_col
        if not col:
            return

        def sort_key(item_id):
            val = self._tree.set(item_id, col)
            if col == "平均スコア":
                try:
                    return float(val)
                except ValueError:
                    return 0.0
            return val.lower()

        children = list(self._tree.get_children(""))
        children.sort(key=sort_key, reverse=self._sort_reverse)
        for i, item_id in enumerate(children):
            self._tree.move(item_id, "", i)

        indicator = " ▼" if self._sort_reverse else " ▲"
        for c in self._cols:
            base = c.rstrip(" ▲▼")
            self._tree.heading(c, text=base + (indicator if c == col else ""),
                               command=lambda x=c: self._sort_by(x))

    def _draw_empty_chart(self):
        self._ax.clear()
        self._ax.text(0.5, 0.5, "データを読み込んでください", ha="center", va="center",
                      transform=self._ax.transAxes, fontsize=12, color="gray")
        self._ax.set_axis_off()
        self._canvas.draw()

    def _open_file(self):
        path = filedialog.askopenfilename(
            initialdir=str(main.DATA_DIR),
            title="サーベイCSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.load_survey(Path(path))
            self._refresh_summary()
            self._refresh_tree()
            self._refresh_chart()
            self._status_var.set(f"読み込み完了: {Path(path).name}  ({len(self._df)} 名)")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _refresh_summary(self):
        score = main.get_overall_score(self._df)
        self._overall_var.set(f"{score:.2f} / 5.00")
        self._respondents_var.set(f"回答数: {len(self._df)} 名")

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        q_df = main.aggregate_by_question(self._df)
        max_score = q_df["平均スコア"].max()
        min_score = q_df["平均スコア"].min()
        for _, row in q_df.iterrows():
            tag = "high" if row["平均スコア"] == max_score else ("low" if row["平均スコア"] == min_score else "")
            self._tree.insert(
                "", tk.END,
                values=(row["設問名"], f"{row['平均スコア']:.2f}"),
                tags=(tag,),
            )
        self._apply_sort()

    def _refresh_chart(self):
        if self._df is None:
            return
        mode = self._view_var.get()
        if mode == VIEW_OPTIONS[0]:
            self._draw_bar_chart()
        else:
            self._draw_radar_chart()

    def _draw_bar_chart(self):
        self._fig.clear()
        self._ax = self._fig.add_subplot(111)
        q_df = main.aggregate_by_question(self._df)
        names = q_df["設問名"].tolist()
        scores = q_df["平均スコア"].tolist()
        colors = ["#5cb85c" if s >= 4.0 else "#f0ad4e" if s >= 3.0 else "#d9534f" for s in scores]
        bars = self._ax.bar(names, scores, color=colors)
        self._ax.bar_label(bars, fmt="%.2f", padding=2, fontsize=8)
        self._ax.set_ylim(0, 5.5)
        self._ax.axhline(y=4.0, color="green", linestyle="--", linewidth=1, alpha=0.5, label="4.0")
        self._ax.axhline(y=3.0, color="orange", linestyle="--", linewidth=1, alpha=0.5, label="3.0")
        self._ax.set_ylabel("平均スコア（5点満点）")
        self._ax.set_title("設問別 平均スコア（全体）")
        self._ax.legend(fontsize=8)
        plt.setp(self._ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
        self._fig.tight_layout()
        self._canvas.draw()

    def _draw_radar_chart(self):
        dept_df = main.aggregate_by_department(self._df)
        q_labels = list(main.QUESTION_LABELS.values())
        n = len(q_labels)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        self._fig.clear()
        self._ax = self._fig.add_subplot(111, polar=True)

        colors = plt.cm.Set1.colors
        for i, (_, row) in enumerate(dept_df.iterrows()):
            dept_name = row["部署"]
            values = [row[q] for q in q_labels]
            values += values[:1]
            self._ax.plot(angles, values, "o-", linewidth=1.5, label=dept_name, color=colors[i % len(colors)])
            self._ax.fill(angles, values, alpha=0.08, color=colors[i % len(colors)])

        self._ax.set_xticks(angles[:-1])
        self._ax.set_xticklabels(q_labels, fontsize=8)
        self._ax.set_ylim(0, 5)
        self._ax.set_title("部署別 スコア比較（レーダー）", pad=16)
        self._ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
        self._fig.tight_layout()
        self._canvas.draw()

    def _save(self):
        if self._df is None:
            messagebox.showwarning("保存エラー", "データがありません")
            return
        try:
            out = main.save_results(self._df)
            messagebox.showinfo("保存完了", f"保存しました:\n{out}")
        except Exception as e:
            messagebox.showerror("保存エラー", str(e))


if __name__ == "__main__":
    app = SurveyApp()
    app.mainloop()
