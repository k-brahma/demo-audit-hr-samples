"""契約書期限管理 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, messagebox

import main

main.init_db()

ROW_COLORS = {
    "期限切れ": "#f8d7da",
    "危険": "#f8d7da",
    "警告": "#fff3cd",
    "正常": "#d4edda",
}

URGENCY_FG = {
    "期限切れ": "#721c24",
    "危険": "#721c24",
    "警告": "#856404",
    "正常": "#155724",
}


class ContractApp(tk.Tk):
    """契約書期限管理メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("契約書 期限管理ツール")
        self.geometry("1000x660")
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # ツールバー
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="➕ 契約追加", command=self._add_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="🗑 削除", command=self._delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="🔄 更新", command=self._refresh).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 CSV出力", command=self._export).pack(side=tk.LEFT, padx=4)

        # 凡例
        legend = ttk.Frame(toolbar)
        legend.pack(side=tk.RIGHT, padx=8)
        for text, bg, fg in [
            ("期限切れ/危険(≤30日)", "#f8d7da", "#721c24"),
            ("警告(≤90日)", "#fff3cd", "#856404"),
            ("正常", "#d4edda", "#155724"),
        ]:
            tk.Label(legend, text=f"  {text}  ", bg=bg, fg=fg,
                     font=("Yu Gothic", 8)).pack(side=tk.LEFT, padx=2)

        # Treeview
        cols = ("id", "契約名", "相手先", "開始日", "終了日", "カテゴリ", "残日数", "緊急度", "備考")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=26)
        widths = [40, 200, 130, 90, 90, 80, 70, 70, 160]
        anchors = [tk.CENTER, tk.W, tk.W, tk.CENTER, tk.CENTER, tk.CENTER, tk.CENTER, tk.CENTER, tk.W]
        for col, w, a in zip(cols, widths, anchors):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=a)

        for tag, bg in ROW_COLORS.items():
            self._tree.tag_configure(tag, background=bg)

        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=4)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=4, padx=(0, 8))

    def _refresh(self):
        self._tree.delete(*self._tree.get_children())
        contracts = main.load_all()
        counts = {"期限切れ": 0, "危険": 0, "警告": 0, "正常": 0}
        for c in contracts:
            tag = c["緊急度"]
            counts[tag] = counts.get(tag, 0) + 1
            days_text = f"{c['残日数']}日" if c["残日数"] >= 0 else f"超過{abs(c['残日数'])}日"
            self._tree.insert(
                "", tk.END,
                values=(c["id"], c["name"], c["counterparty"],
                        c["start_date"], c["end_date"], c["category"],
                        days_text, c["緊急度"], c["notes"]),
                tags=(tag,),
            )
        self.title(
            f"契約書 期限管理ツール  ─  "
            f"期限切れ/危険:{counts.get('期限切れ',0)+counts.get('危険',0)}件  "
            f"警告:{counts.get('警告',0)}件  正常:{counts.get('正常',0)}件"
        )

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("選択エラー", "契約を選択してください")
            return None
        return int(self._tree.item(sel[0], "values")[0])

    def _add_dialog(self):
        dlg = _AddContractDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            main.add_contract(*dlg.result)
            self._refresh()

    def _delete(self):
        contract_id = self._selected_id()
        if contract_id is None:
            return
        if messagebox.askyesno("削除確認", f"ID={contract_id} を削除しますか？"):
            main.delete_contract(contract_id)
            self._refresh()

    def _export(self):
        try:
            out = main.export_results()
            messagebox.showinfo("出力完了", f"CSV出力しました:\n{out}")
        except Exception as e:
            messagebox.showerror("エラー", str(e))


class _AddContractDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("契約追加")
        self.resizable(False, False)
        self.result = None
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=14)
        frm.pack()
        self._vars = {}
        fields = [
            ("契約名", "name", 30),
            ("相手先", "counterparty", 20),
            ("開始日 (YYYY-MM-DD)", "start_date", 14),
            ("終了日 (YYYY-MM-DD)", "end_date", 14),
            ("備考", "notes", 30),
        ]
        for i, (label, key, w) in enumerate(fields):
            ttk.Label(frm, text=label, width=22, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            ttk.Entry(frm, textvariable=var, width=w).grid(row=i, column=1, padx=8, pady=3, sticky=tk.W)
            self._vars[key] = var

        ttk.Label(frm, text="カテゴリ", width=22, anchor=tk.W).grid(row=5, column=0, sticky=tk.W, pady=3)
        self._category = tk.StringVar(value=main.CATEGORY_OPTIONS[0])
        ttk.Combobox(frm, textvariable=self._category,
                     values=main.CATEGORY_OPTIONS, width=14, state="readonly").grid(row=5, column=1, sticky=tk.W, padx=8)

        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frm, text="追加", command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frm, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        required = ["name", "counterparty", "start_date", "end_date"]
        if not all(self._vars[k].get().strip() for k in required):
            messagebox.showwarning("入力エラー", "必須フィールドを入力してください", parent=self)
            return
        try:
            from datetime import datetime
            for key in ("start_date", "end_date"):
                datetime.strptime(self._vars[key].get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("日付エラー", "日付は YYYY-MM-DD 形式で入力してください", parent=self)
            return
        self.result = (
            self._vars["name"].get().strip(),
            self._vars["counterparty"].get().strip(),
            self._vars["start_date"].get().strip(),
            self._vars["end_date"].get().strip(),
            self._category.get(),
            self._vars["notes"].get().strip(),
        )
        self.destroy()


if __name__ == "__main__":
    app = ContractApp()
    app.mainloop()
