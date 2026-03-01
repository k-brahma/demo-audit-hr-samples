"""勤怠データ異常検知 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"


class AttendanceApp(tk.Tk):
    """勤怠データ異常検知メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("勤怠データ異常検知ツール")
        self.geometry("1000x640")
        self._df = None
        self._sort_col = ""
        self._sort_reverse = False
        self._build_ui()

    def _build_ui(self):
        # ツールバー
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=4)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # 凡例ラベル
        legend = ttk.Frame(toolbar)
        legend.pack(side=tk.RIGHT, padx=8)
        for text, color in [("正常", "#5cb85c"), ("警告 ≥45h", "#f0ad4e"), ("危険 ≥80h", "#d9534f")]:
            lbl = tk.Label(legend, text=f"  {text}  ", bg=color, fg="white", font=("Yu Gothic", 9, "bold"))
            lbl.pack(side=tk.LEFT, padx=2)

        # メイン分割ペイン
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: Treeview
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        cols = ("社員ID", "氏名", "部署", "年月", "月次残業時間", "ステータス")
        self._cols = cols
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=22)
        widths = [70, 80, 80, 90, 110, 80]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.tag_configure("正常", background="#d4edda")
        self._tree.tag_configure("警告", background="#fff3cd")
        self._tree.tag_configure("危険", background="#f8d7da")

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

    _STATUS_ORDER = {"危険": 0, "警告": 1, "正常": 2}

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
            if col == "月次残業時間":
                try:
                    return float(val.replace(" h", ""))
                except ValueError:
                    return 0.0
            if col == "ステータス":
                return self._STATUS_ORDER.get(val, 99)
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
            title="勤怠CSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.analyze(Path(path))
            self._refresh_tree()
            self._refresh_chart()
            self._status_var.set(f"読み込み完了: {Path(path).name}  ({len(self._df)} 件)")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _refresh_chart(self):
        self._ax.clear()
        df = self._df.copy()
        color_map = {"正常": "#5cb85c", "警告": "#f0ad4e", "危険": "#d9534f"}
        colors = df["ステータス"].map(color_map).fillna("#aaaaaa")
        labels = df["氏名"] + "\n(" + df["年月"] + ")"

        self._ax.barh(labels, df["月次残業時間"], color=colors)
        self._ax.axvline(x=main.OVERTIME_WARNING, color="orange", linestyle="--",
                         linewidth=1.5, label=f"警告 {main.OVERTIME_WARNING}h")
        self._ax.axvline(x=main.OVERTIME_DANGER, color="red", linestyle="--",
                         linewidth=1.5, label=f"危険 {main.OVERTIME_DANGER}h")
        self._ax.set_xlabel("月次残業時間（時間）")
        self._ax.set_title("月次残業時間サマリー")
        self._ax.legend(fontsize=8)
        self._fig.tight_layout()
        self._canvas.draw()

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        for _, row in self._df.iterrows():
            tag = row["ステータス"]
            self._tree.insert(
                "", tk.END,
                values=(
                    row["社員ID"], row["氏名"], row["部署"], row["年月"],
                    f"{row['月次残業時間']:.1f} h", row["ステータス"],
                ),
                tags=(tag,),
            )
        self._apply_sort()

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
    app = AttendanceApp()
    app.mainloop()
