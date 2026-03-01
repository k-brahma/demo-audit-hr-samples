"""採用コスト可視化 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"


class RecruitmentApp(tk.Tk):
    """採用コスト可視化メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("採用コスト可視化ツール")
        self.geometry("1040px".replace("px", "")) if False else None
        self.geometry("1040x660")
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
        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=4)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # サマリーカード
        self._summary_frame = ttk.LabelFrame(self, text="サマリー", padding=6)
        self._summary_frame.pack(fill=tk.X, padx=8, pady=4)
        self._summary_labels = {}
        for key in ["総応募数", "総採用数", "総費用(万円)", "平均CPA(万円)", "全体採用率(%)"]:
            frm = ttk.Frame(self._summary_frame)
            frm.pack(side=tk.LEFT, padx=16)
            ttk.Label(frm, text=key, font=("Yu Gothic", 8), foreground="gray").pack()
            lbl = ttk.Label(frm, text="—", font=("Yu Gothic", 14, "bold"))
            lbl.pack()
            self._summary_labels[key] = lbl

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: Treeview
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        cols = ("媒体名", "応募数", "採用数", "費用(万円)", "CPA(万円)", "採用率(%)")
        self._cols = cols
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        widths = [150, 70, 70, 100, 100, 90]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.column("媒体名", anchor=tk.W)
        self._tree.tag_configure("best", background="#d4edda")

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: グラフ
        right = ttk.Frame(pane)
        pane.add(right, weight=1)
        self._fig, self._ax = plt.subplots(figsize=(5, 5))
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_empty_chart()

    _INT_COLS = {"応募数", "採用数"}
    _FLOAT_COLS = {"費用(万円)", "採用率(%)"}

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
            if col in self._INT_COLS:
                try:
                    return int(val)
                except ValueError:
                    return 0
            if col in self._FLOAT_COLS:
                try:
                    return float(val)
                except ValueError:
                    return 0.0
            if col == "CPA(万円)":
                if val == "採用なし":
                    return float("inf")
                try:
                    return float(val)
                except ValueError:
                    return float("inf")
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
            title="採用CSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.analyze(Path(path))
            self._refresh_summary()
            self._refresh_tree()
            self._refresh_chart()
            self._status_var.set(f"読み込み完了: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _refresh_summary(self):
        summary = main.get_summary(self._df)
        for key, lbl in self._summary_labels.items():
            lbl.configure(text=str(summary.get(key, "—")))

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        hired = self._df[self._df["採用数"] > 0]
        min_cpa = hired["CPA(万円)"].min() if not hired.empty else None
        for _, row in self._df.iterrows():
            no_hire = row["採用数"] == 0
            tag = "best" if not no_hire and row["CPA(万円)"] == min_cpa else ""
            cpa_display = "採用なし" if no_hire else row["CPA(万円)"]
            self._tree.insert(
                "", tk.END,
                values=(
                    row["媒体名"], int(row["応募数"]), int(row["採用数"]),
                    row["費用(万円)"], cpa_display, row["採用率(%)"],
                ),
                tags=(tag,),
            )
        self._apply_sort()

    def _refresh_chart(self):
        self._ax.clear()
        df = self._df[self._df["採用数"] > 0].copy()
        colors = ["#5cb85c" if v == df["CPA(万円)"].min() else "#4a90d9" for v in df["CPA(万円)"]]
        bars = self._ax.bar(df["媒体名"], df["CPA(万円)"], color=colors)
        self._ax.bar_label(bars, fmt="%.1f万", padding=2, fontsize=8)
        self._ax.set_xlabel("媒体名")
        self._ax.set_ylabel("CPA（万円）")
        self._ax.set_title("媒体別 一人当たり採用コスト（CPA）")
        plt.setp(self._ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
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
    app = RecruitmentApp()
    app.mainloop()
