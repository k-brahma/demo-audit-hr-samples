"""リスク評価マトリクス GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"

CATEGORY_OPTIONS = ["財務", "情報", "法務", "人事", "業務", "その他"]


class RiskMatrixApp(tk.Tk):
    """リスク評価マトリクスメインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("リスク評価マトリクス自動生成ツール")
        self.geometry("1100x700")
        self._df = None
        self._sort_col = ""
        self._sort_reverse = False
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        """ウィンドウ閉じるボタン押下時の後処理。"""
        plt.close("all")
        self.destroy()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 PNG保存", command=self._save_png).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="📋 CSVエクスポート", command=self._save_csv).pack(side=tk.LEFT, padx=4)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # リスク追加フォーム
        form = ttk.LabelFrame(self, text="リスク追加", padding=6)
        form.pack(fill=tk.X, padx=8, pady=2)
        self._form_vars = {}
        labels_widths = [("分類", 8), ("リスク内容", 30), ("担当者", 10)]
        for i, (label, w) in enumerate(labels_widths):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, padx=4, sticky=tk.W)
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=w).grid(row=0, column=i * 2 + 1, padx=4)
            self._form_vars[label] = var

        ttk.Label(form, text="発生確率(1-5)").grid(row=0, column=6, padx=4)
        self._prob_var = tk.IntVar(value=3)
        ttk.Spinbox(form, from_=1, to=5, textvariable=self._prob_var, width=4).grid(row=0, column=7, padx=4)

        ttk.Label(form, text="影響度(1-5)").grid(row=0, column=8, padx=4)
        self._impact_var = tk.IntVar(value=3)
        ttk.Spinbox(form, from_=1, to=5, textvariable=self._impact_var, width=4).grid(row=0, column=9, padx=4)

        ttk.Button(form, text="追加", command=self._add_risk).grid(row=0, column=10, padx=8)

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: Treeview
        left = ttk.Frame(pane)
        pane.add(left, weight=1)
        cols = ("リスクID", "分類", "リスク内容", "発生確率", "影響度", "スコア", "担当者")
        self._cols = cols
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=20)
        widths = [70, 70, 200, 70, 70, 60, 90]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.column("リスク内容", anchor=tk.W)
        self._tree.tag_configure("高", background="#f8d7da")
        self._tree.tag_configure("中", background="#fff3cd")

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: ヒートマップ
        right = ttk.Frame(pane)
        pane.add(right, weight=1)
        self._fig, self._ax = plt.subplots(figsize=(5, 5))
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_empty_chart()

    def _draw_empty_chart(self):
        self._ax.clear()
        self._ax.text(0.5, 0.5, "データを読み込んでください", ha="center", va="center",
                      transform=self._ax.transAxes, fontsize=11, color="gray")
        self._ax.set_axis_off()
        self._canvas.draw()

    def _open_file(self):
        path = filedialog.askopenfilename(
            initialdir=str(main.DATA_DIR),
            title="リスクCSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.load_risks(Path(path))
            self._refresh_tree()
            self._refresh_chart()
            self._status_var.set(f"読み込み完了: {Path(path).name}  ({len(self._df)} 件)")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _add_risk(self):
        if self._df is None:
            messagebox.showwarning("エラー", "先にCSVを読み込んでください")
            return
        category = self._form_vars["分類"].get().strip()
        content = self._form_vars["リスク内容"].get().strip()
        owner = self._form_vars["担当者"].get().strip()
        if not category or not content:
            messagebox.showwarning("入力エラー", "分類とリスク内容を入力してください")
            return
        self._df = main.add_risk(
            self._df, category, content,
            self._prob_var.get(), self._impact_var.get(), owner
        )
        self._refresh_tree()
        self._refresh_chart()
        for var in self._form_vars.values():
            var.set("")

    _INT_COLS = {"発生確率", "影響度", "スコア"}

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        for _, row in self._df.sort_values("リスクスコア", ascending=False).iterrows():
            level = main.classify_risk_level(int(row["リスクスコア"]))
            self._tree.insert(
                "", tk.END,
                values=(row["リスクID"], row["分類"], row["リスク内容"],
                        row["発生確率"], row["影響度"], row["リスクスコア"], row["担当者"]),
                tags=(level,),
            )
        self._apply_sort()

    def _sort_by(self, col: str) -> None:
        """カラムヘッダーをクリックしたときの並べ替え処理。

        :param col: ソート対象カラム名
        :type col: str
        """
        self._sort_reverse = (self._sort_col == col) and not self._sort_reverse
        self._sort_col = col
        self._apply_sort()

    def _apply_sort(self) -> None:
        """現在の _sort_col / _sort_reverse 状態でツリーを並べ替える。"""
        col = self._sort_col
        if not col:
            return

        def sort_key(item_id):
            val = self._tree.set(item_id, col)
            if col in self._INT_COLS:
                try:
                    return int(val)
                except ValueError:
                    return 0
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

    def _refresh_chart(self):
        self._ax.clear()
        matrix = main.build_heatmap_matrix(self._df)

        # 背景色マトリクス（スコア = 行*列の重み）
        bg = np.array([[r * c for c in range(1, 6)] for r in range(1, 6)], dtype=float)
        self._ax.imshow(bg, cmap="RdYlGn_r", vmin=1, vmax=25, alpha=0.5, origin="lower")

        # リスク件数テキスト
        for r in range(5):
            for c in range(5):
                count = matrix[r][c]
                text = str(count) if count > 0 else "·"
                size = 14 if count > 0 else 10
                color = "black" if count > 0 else "#bbbbbb"
                self._ax.text(c, r, text, ha="center", va="center", fontsize=size,
                               fontweight="bold" if count > 0 else "normal", color=color)

        self._ax.set_xticks(range(5))
        self._ax.set_yticks(range(5))
        self._ax.set_xticklabels(["1\n非常に低い", "2\n低い", "3\n中程度", "4\n高い", "5\n非常に高い"], fontsize=7)
        self._ax.set_yticklabels(["1\n非常に低い", "2\n低い", "3\n中程度", "4\n高い", "5\n非常に高い"], fontsize=7)
        self._ax.set_xlabel("影響度", fontsize=10)
        self._ax.set_ylabel("発生確率", fontsize=10)
        self._ax.set_title(f"リスクマトリクス（全{len(self._df)}件）")
        self._fig.tight_layout()
        self._canvas.draw()

    def _save_png(self):
        if self._df is None:
            messagebox.showwarning("エラー", "データがありません")
            return
        main.RESULTS_DIR.mkdir(exist_ok=True)
        out = main.RESULTS_DIR / "risk_matrix.png"
        self._fig.savefig(out, dpi=150, bbox_inches="tight")
        messagebox.showinfo("保存完了", f"PNG保存しました:\n{out}")

    def _save_csv(self):
        if self._df is None:
            messagebox.showwarning("エラー", "データがありません")
            return
        try:
            out = main.save_results(self._df)
            messagebox.showinfo("保存完了", f"CSV保存しました:\n{out}")
        except Exception as e:
            messagebox.showerror("保存エラー", str(e))


if __name__ == "__main__":
    app = RiskMatrixApp()
    app.mainloop()
