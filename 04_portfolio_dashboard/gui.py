"""株式ポートフォリオ損益ダッシュボード GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import main

matplotlib.rcParams["font.family"] = "Yu Gothic"


class PortfolioApp(tk.Tk):
    """ポートフォリオダッシュボードメインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("株式ポートフォリオ 損益ダッシュボード")
        self.geometry("1100x680")
        self._df = None
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="📂 CSVを開く", command=self._open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 結果を保存", command=self._save).pack(side=tk.LEFT, padx=4)
        self._status_var = tk.StringVar(value="CSVファイルを読み込んでください")
        ttk.Label(toolbar, textvariable=self._status_var, foreground="gray").pack(side=tk.LEFT, padx=12)

        # サマリーカード
        summary_frame = ttk.LabelFrame(self, text="ポートフォリオ サマリー", padding=6)
        summary_frame.pack(fill=tk.X, padx=8, pady=4)
        self._summary_labels = {}
        for key in ["総取得額", "総評価額", "総損益額", "損益率(%)"]:
            frm = ttk.Frame(summary_frame)
            frm.pack(side=tk.LEFT, padx=20)
            ttk.Label(frm, text=key, font=("Yu Gothic", 8), foreground="gray").pack()
            lbl = ttk.Label(frm, text="—", font=("Yu Gothic", 15, "bold"))
            lbl.pack()
            self._summary_labels[key] = lbl

        # メイン分割
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 左: Treeview
        left = ttk.Frame(pane)
        pane.add(left, weight=3)
        cols = ("銘柄名", "保有数", "平均取得単価", "現在価格", "評価額", "損益額", "損益率(%)", "配分(%)")
        self._tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        widths = [130, 60, 110, 90, 100, 100, 80, 70]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.column("銘柄名", anchor=tk.W)
        self._tree.tag_configure("profit", foreground="#c0392b")
        self._tree.tag_configure("loss", foreground="#2980b9")

        vsb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 右: 円グラフ
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._fig, self._ax = plt.subplots(figsize=(4.5, 4.5))
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
            title="ポートフォリオCSVを選択",
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
        pnl = summary["総損益額"]
        for key, lbl in self._summary_labels.items():
            val = summary[key]
            if key in ("総取得額", "総評価額", "総損益額"):
                text = f"¥{val:,.0f}"
            else:
                text = f"{val:+.2f}%" if key == "損益率(%)" else str(val)
            color = "#c0392b" if key in ("総損益額", "損益率(%)") and pnl >= 0 else "#2980b9"
            lbl.configure(text=text, foreground=color if key in ("総損益額", "損益率(%)") else "black")

    def _refresh_tree(self):
        self._tree.delete(*self._tree.get_children())
        for _, row in self._df.iterrows():
            tag = "profit" if row["損益額"] >= 0 else "loss"
            self._tree.insert(
                "", tk.END,
                values=(
                    row["銘柄名"],
                    int(row["保有数"]),
                    f"¥{row['平均取得単価']:,.0f}",
                    f"¥{row['現在価格']:,.0f}",
                    f"¥{row['評価額']:,.0f}",
                    f"¥{row['損益額']:+,.0f}",
                    f"{row['損益率(%)']:+.2f}%",
                    f"{row['配分(%)']:.1f}%",
                ),
                tags=(tag,),
            )

    def _refresh_chart(self):
        self._ax.clear()
        df = self._df.sort_values("評価額", ascending=False)
        sizes = df["評価額"].values
        labels = df["銘柄名"].values
        self._ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90,
                     textprops={"fontsize": 8})
        self._ax.set_title("資産配分（評価額ベース）")
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
    app = PortfolioApp()
    app.mainloop()
