"""KPI トラッカー GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"


class KPITrackerApp(tk.Tk):
    """KPIトラッカーメインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("KPI トラッカー")
        self.geometry("1060x680")
        self._df = None
        self._analyzed = None
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=4)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: KPIセレクタ + サマリーテーブル
        left = ttk.Frame(pane)
        pane.add(left, weight=1)

        select_frame = ttk.LabelFrame(left, text="KPI選択", padding=6)
        select_frame.pack(fill=tk.X, pady=(0, 6))
        self._kpi_var = tk.StringVar()
        self._kpi_cb = ttk.Combobox(select_frame, textvariable=self._kpi_var,
                                     state="readonly", width=22)
        self._kpi_cb.pack(side=tk.LEFT, padx=4)
        self._kpi_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_chart())

        # 最新月サマリーテーブル
        summary_frame = ttk.LabelFrame(left, text="最新月サマリー", padding=4)
        summary_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("KPI名", "カテゴリ", "目標", "実績", "達成率(%)", "ステータス")
        self._tree = ttk.Treeview(summary_frame, columns=cols, show="headings", height=18)
        widths = [120, 80, 90, 90, 90, 70]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.column("KPI名", anchor=tk.W)
        self._tree.tag_configure("達成", background="#d4edda")
        self._tree.tag_configure("警告", background="#fff3cd")
        self._tree.tag_configure("危険", background="#f8d7da")

        vsb = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: 折れ線グラフ
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._fig, self._ax = plt.subplots(figsize=(6, 5))
        self._canvas = FigureCanvasTkAgg(self._fig, master=right)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._draw_empty_chart()

    def _draw_empty_chart(self):
        self._ax.clear()
        self._ax.text(0.5, 0.5, "KPIを選択してください", ha="center", va="center",
                      transform=self._ax.transAxes, fontsize=12, color="gray")
        self._ax.set_axis_off()
        self._canvas.draw()

    def _open_file(self):
        path = filedialog.askopenfilename(
            initialdir=str(main.DATA_DIR),
            title="KPI CSVを選択",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            self._df = main.load_kpi(Path(path))
            self._analyzed = main.calculate_achievement(self._df)
            self._refresh_kpi_selector()
            self._refresh_summary_tree()
            self._status_var.set(f"読み込み完了: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("読み込みエラー", str(e))

    def _refresh_kpi_selector(self):
        names = main.get_kpi_names(self._analyzed)
        self._kpi_cb.configure(values=names)
        if names:
            self._kpi_var.set(names[0])
            self._refresh_chart()

    def _refresh_summary_tree(self):
        self._tree.delete(*self._tree.get_children())
        summary = main.get_latest_summary(self._analyzed)
        for _, row in summary.iterrows():
            tag = row["ステータス"]
            self._tree.insert(
                "", tk.END,
                values=(
                    row["KPI名"], row["カテゴリ"],
                    f"{row['目標']:,.0f}", f"{row['実績']:,.0f}",
                    f"{row['達成率(%)']:.1f}%", row["ステータス"],
                ),
                tags=(tag,),
            )

    def _refresh_chart(self):
        if self._analyzed is None:
            return
        kpi = self._kpi_var.get()
        if not kpi:
            return
        trend = main.get_kpi_trend(self._analyzed, kpi)

        self._ax.clear()
        x = trend["年月"].tolist()
        target = trend["目標"].tolist()
        actual = trend["実績"].tolist()
        rate = trend["達成率(%)"].tolist()

        self._ax.plot(x, target, "o--", color="#aaaaaa", label="目標", linewidth=1.5)
        colors = ["#c0392b" if r < main.ACHIEVEMENT_WARNING else "#27ae60" for r in rate]
        for i in range(len(x) - 1):
            self._ax.plot(x[i:i+2], actual[i:i+2], color=colors[i], linewidth=2)
        self._ax.scatter(x, actual, color=colors, zorder=5, s=50)

        # 達成率をデータ点に表示
        for xi, yi, ri in zip(x, actual, rate):
            self._ax.annotate(f"{ri:.0f}%", (xi, yi), textcoords="offset points",
                              xytext=(0, 8), fontsize=8, ha="center")

        self._ax.axhline(y=0, color="black", linewidth=0.5)
        self._ax.set_title(f"KPI推移: {kpi}")
        self._ax.set_xlabel("年月")
        self._ax.set_ylabel("値")
        self._ax.legend(fontsize=9)
        plt.setp(self._ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
        self._fig.tight_layout()
        self._canvas.draw()

    def _save(self):
        if self._analyzed is None:
            messagebox.showwarning("保存エラー", "データがありません")
            return
        try:
            out = main.save_results(self._analyzed)
            messagebox.showinfo("保存完了", f"保存しました:\n{out}")
        except Exception as e:
            messagebox.showerror("保存エラー", str(e))


if __name__ == "__main__":
    app = KPITrackerApp()
    app.mainloop()
