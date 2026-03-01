"""内部統制チェックリスト GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import main

main.init_db()


class ChecklistApp(tk.Tk):
    """内部統制チェックリストメインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("内部統制チェックリスト")
        self.geometry("1000x660")
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # ツールバー
        toolbar = ttk.Frame(self, padding=4)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="➕ 項目追加", command=self._add_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="✏️ ステータス更新", command=self._update_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="🗑 削除", command=self._delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 CSV出力", command=self._export).pack(side=tk.LEFT, padx=4)

        # 進捗バーエリア
        prog_frame = ttk.LabelFrame(self, text="進捗", padding=6)
        prog_frame.pack(fill=tk.X, padx=8, pady=4)
        self._prog_var = tk.DoubleVar(value=0)
        self._prog_label = tk.StringVar(value="0 / 0 完了  (0.0%)")
        ttk.Progressbar(prog_frame, variable=self._prog_var, maximum=100,
                        length=600, mode="determinate").pack(side=tk.LEFT, padx=4)
        ttk.Label(prog_frame, textvariable=self._prog_label).pack(side=tk.LEFT, padx=8)

        # Treeview
        cols = ("id", "カテゴリ", "チェック項目", "担当者", "優先度", "ステータス", "コメント")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=24)
        widths = [40, 90, 320, 100, 60, 80, 200]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=tk.W if w > 80 else tk.CENTER)
        self._tree.column("id", width=40, anchor=tk.CENTER)

        self._tree.tag_configure("完了", foreground="#555555")
        self._tree.tag_configure("該当なし", foreground="#888888")
        self._tree.tag_configure("進行中", foreground="#0066cc")
        self._tree.tag_configure("高", background="#ffeeba")

        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=4)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=4, padx=(0, 8))

    def _refresh(self):
        self._tree.delete(*self._tree.get_children())
        rows = main.load_all()
        for r in rows:
            tags = []
            if r["status"] in ("完了", "該当なし"):
                tags.append(r["status"])
            elif r["status"] == "進行中":
                tags.append("進行中")
            if r["priority"] == "高" and r["status"] == "未着手":
                tags.append("高")
            self._tree.insert(
                "", tk.END,
                values=(r["id"], r["category"], r["item"], r["responsible"],
                        r["priority"], r["status"], r["comment"]),
                tags=tuple(tags),
            )
        prog = main.get_progress()
        self._prog_var.set(prog["rate"])
        self._prog_label.set(
            f"{prog['completed']} / {prog['total']} 完了  ({prog['rate']:.1f}%)"
        )

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("選択エラー", "項目を選択してください")
            return None
        return int(self._tree.item(sel[0], "values")[0])

    def _add_dialog(self):
        dlg = _AddItemDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            main.add_item(*dlg.result)
            self._refresh()

    def _update_dialog(self):
        item_id = self._selected_id()
        if item_id is None:
            return
        dlg = _UpdateStatusDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            status, comment = dlg.result
            main.update_status(item_id, status, comment)
            self._refresh()

    def _delete(self):
        item_id = self._selected_id()
        if item_id is None:
            return
        if messagebox.askyesno("確認", f"ID={item_id} を削除しますか？"):
            main.delete_item(item_id)
            self._refresh()

    def _export(self):
        try:
            out = main.export_results()
            messagebox.showinfo("出力完了", f"CSV出力しました:\n{out}")
        except Exception as e:
            messagebox.showerror("エラー", str(e))


class _AddItemDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("項目追加")
        self.resizable(False, False)
        self.result = None
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack()
        fields = [("カテゴリ", "category"), ("チェック項目", "item"),
                  ("担当者", "responsible")]
        self._vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            ttk.Entry(frm, textvariable=var, width=30).grid(row=i, column=1, padx=8, pady=3)
            self._vars[key] = var

        ttk.Label(frm, text="優先度").grid(row=3, column=0, sticky=tk.W, pady=3)
        self._priority = tk.StringVar(value="中")
        ttk.Combobox(frm, textvariable=self._priority,
                     values=main.PRIORITY_OPTIONS, width=10, state="readonly").grid(row=3, column=1, sticky=tk.W, padx=8)

        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=4, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frm, text="追加", command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frm, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        vals = [self._vars[k].get().strip() for k in ("category", "item", "responsible")]
        if not all(vals):
            messagebox.showwarning("入力エラー", "全フィールドを入力してください", parent=self)
            return
        self.result = (*vals, self._priority.get())
        self.destroy()


class _UpdateStatusDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("ステータス更新")
        self.resizable(False, False)
        self.result = None
        self._build()
        self.grab_set()

    def _build(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack()
        ttk.Label(frm, text="ステータス").grid(row=0, column=0, sticky=tk.W, pady=4)
        self._status = tk.StringVar(value="完了")
        ttk.Combobox(frm, textvariable=self._status,
                     values=main.STATUS_OPTIONS, width=12, state="readonly").grid(row=0, column=1, padx=8)

        ttk.Label(frm, text="コメント").grid(row=1, column=0, sticky=tk.W, pady=4)
        self._comment = tk.StringVar()
        ttk.Entry(frm, textvariable=self._comment, width=30).grid(row=1, column=1, padx=8)

        btn_frm = ttk.Frame(frm)
        btn_frm.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frm, text="更新", command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frm, text="キャンセル", command=self.destroy).pack(side=tk.LEFT)

    def _ok(self):
        self.result = (self._status.get(), self._comment.get().strip())
        self.destroy()


if __name__ == "__main__":
    app = ChecklistApp()
    app.mainloop()
