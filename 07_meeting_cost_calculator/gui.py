"""会議コスト計算機 GUI アプリ。"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import main


class MeetingCostApp(tk.Tk):
    """会議コスト計算機メインウィンドウ。"""

    def __init__(self):
        super().__init__()
        self.title("会議コスト計算機")
        self.geometry("520x560")
        self.resizable(False, False)
        self._running = False
        self._start_time = None
        self._elapsed = 0.0
        self._after_id = None
        self._build_ui()

    def _build_ui(self):
        # プリセット
        preset_frame = ttk.LabelFrame(self, text="プリセット", padding=8)
        preset_frame.pack(fill=tk.X, padx=16, pady=(12, 4))
        for preset in main.PRESETS:
            ttk.Button(
                preset_frame, text=preset["名前"],
                command=lambda p=preset: self._apply_preset(p),
            ).pack(side=tk.LEFT, padx=4)

        # 入力フォーム
        form = ttk.LabelFrame(self, text="会議設定", padding=12)
        form.pack(fill=tk.X, padx=16, pady=4)
        self._participants = tk.IntVar(value=6)
        self._hourly_rate = tk.IntVar(value=4000)

        rows = [
            ("参加人数（人）", self._participants, 1, 50),
            ("平均時給（円）", self._hourly_rate, 500, 50000),
        ]
        for label, var, from_, to in rows:
            frm = ttk.Frame(form)
            frm.pack(fill=tk.X, pady=4)
            ttk.Label(frm, text=label, width=18).pack(side=tk.LEFT)
            ttk.Spinbox(frm, from_=from_, to=to, textvariable=var,
                        increment=1, width=8).pack(side=tk.LEFT, padx=8)

        # タイマー表示
        timer_frame = ttk.LabelFrame(self, text="リアルタイム計測", padding=12)
        timer_frame.pack(fill=tk.X, padx=16, pady=8)

        self._elapsed_var = tk.StringVar(value="00:00:00")
        ttk.Label(timer_frame, text="経過時間").pack()
        ttk.Label(timer_frame, textvariable=self._elapsed_var,
                  font=("Courier New", 28, "bold"), foreground="#333333").pack()

        # コスト表示（大きく）
        cost_frame = ttk.Frame(self)
        cost_frame.pack(pady=8)
        ttk.Label(cost_frame, text="累計会議コスト", font=("Yu Gothic", 11)).pack()
        self._cost_var = tk.StringVar(value="¥0")
        self._cost_label = tk.Label(
            cost_frame, textvariable=self._cost_var,
            font=("Courier New", 40, "bold"), foreground="#c0392b",
        )
        self._cost_label.pack()

        # 参考メモ
        self._note_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self._note_var, foreground="gray",
                  font=("Yu Gothic", 9)).pack()

        # ボタン
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=12)
        self._start_btn = ttk.Button(btn_frame, text="▶ 開始", command=self._toggle, width=12)
        self._start_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="⏹ リセット", command=self._reset, width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="💾 ログ保存", command=self._save_log, width=12).pack(side=tk.LEFT, padx=6)

    def _apply_preset(self, preset: dict):
        self._participants.set(preset["人数"])
        self._hourly_rate.set(preset["時給"])
        self._note_var.set(f"プリセット「{preset['名前']}」を適用（想定 {preset['分数']} 分）")

    def _toggle(self):
        if self._running:
            self._running = False
            self._start_btn.configure(text="▶ 再開")
            if self._after_id:
                self.after_cancel(self._after_id)
        else:
            self._running = True
            self._start_btn.configure(text="⏸ 一時停止")
            self._last_tick = datetime.now()
            self._tick()

    def _tick(self):
        if not self._running:
            return
        now = datetime.now()
        self._elapsed += (now - self._last_tick).total_seconds()
        self._last_tick = now

        cost = main.calculate_cost(
            self._participants.get(), self._hourly_rate.get(), self._elapsed
        )
        self._elapsed_var.set(main.format_elapsed(self._elapsed))
        self._cost_var.set(main.format_cost(cost))

        # コスト高騰で色変化
        if cost >= 50000:
            self._cost_label.configure(foreground="#8b0000")
        elif cost >= 10000:
            self._cost_label.configure(foreground="#c0392b")
        else:
            self._cost_label.configure(foreground="#e67e22")

        self._after_id = self.after(500, self._tick)

    def _reset(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
        self._elapsed = 0.0
        self._elapsed_var.set("00:00:00")
        self._cost_var.set("¥0")
        self._cost_label.configure(foreground="#c0392b")
        self._start_btn.configure(text="▶ 開始")

    def _save_log(self):
        if self._elapsed < 1:
            messagebox.showwarning("保存エラー", "計測を開始してください")
            return
        cost = main.calculate_cost(
            self._participants.get(), self._hourly_rate.get(), self._elapsed
        )
        record = {
            "日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "参加人数": self._participants.get(),
            "平均時給": self._hourly_rate.get(),
            "経過時間": main.format_elapsed(self._elapsed),
            "コスト": round(cost, 0),
        }
        try:
            out = main.save_log(record)
            messagebox.showinfo("保存完了", f"ログを保存しました:\n{out}")
        except Exception as e:
            messagebox.showerror("保存エラー", str(e))


if __name__ == "__main__":
    app = MeetingCostApp()
    app.mainloop()
