"""給与バンド分析 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"

GROUP_OPTIONS = ["等級別", "部署別"]


class SalaryApp(tk.Tk):
    """給与バンド分析メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("給与バンド分析ツール")
        self.geometry("1060x680")
        self._df = None
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)

        ttk.Label(toolbar, text="表示グループ:").pack(side=tk.LEFT, padx=(16, 4))
        self._group_var = tk.StringVar(value=GROUP_OPTIONS[0])
        cb = ttk.Combobox(toolbar, textvariable=self._group_var,
                          values=GROUP_OPTIONS, width=10, state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_chart())

        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=8)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: 統計Treeview
        left = ttk.LabelFrame(pane, text="統計サマリー（等級別）", padding=4)
        pane.add(left, weight=1)

        cols = ("等級", "最小値", "最大値", "平均値", "中央値", "人数")
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=20)
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=80, anchor=tk.CENTER)
        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: ボックスプロット
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._fig, self._ax = plt.subplots(figsize=(6, 5))
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_empty_chart()

    def _draw_empty_chart(self):
        self._ax.clear()
        self._ax.text(0.5, 0.5, "データを読み込んでください", ha="center", va="center",
                      transform=self._ax.transAxes, fontsize=12, color="gray")
        self._ax.set_axis_off()
        self._canvas.draw()

    def _open_file(self):
        path = filedialog.askopenfilename(
            initialdir=str(main.DATA_DIR),
            title="給与CSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.load_salary(Path(path))
            self._refresh_tree()
            self._refresh_chart()
            self._status_var.set(f"読み込み完了: {Path(path).name}  ({len(self._df)} 名)")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        stats = main.get_grade_stats(self._df)
        for _, row in stats.iterrows():
            self._tree.insert(
                "", tk.END,
                values=(
                    f"等級{row['等級']}",
                    f"{row['最小値']:,}万",
                    f"{row['最大値']:,}万",
                    f"{row['平均値']:,}万",
                    f"{row['中央値']:,}万",
                    f"{int(row['人数'])}名",
                ),
            )

    def _refresh_chart(self):
        if self._df is None:
            return
        self._ax.clear()
        group_label = self._group_var.get()
        group_col = "等級" if group_label == "等級別" else "部署"
        data = main.get_boxplot_data(self._df, group_col)

        labels = list(data.keys())
        values = list(data.values())
        bp = self._ax.boxplot(values, labels=labels, patch_artist=True, notch=False)

        colors = plt.cm.Set2.colors
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)

        self._ax.set_ylabel("年収（万円）")
        self._ax.set_title(f"年収分布 ─ {group_label}")
        self._ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        if group_col == "部署":
            plt.setp(self._ax.get_xticklabels(), rotation=20, ha="right", fontsize=9)
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
    app = SalaryApp()
    app.mainloop()
