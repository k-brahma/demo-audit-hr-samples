"""会議コスト計算機 デモ用モック画面。

スクリーンショット撮影などのデモ用途向けに、
時間経過を待たずに実行中の状態を再現する。

起動すると週次MTG相当の設定・47分経過・タイマー稼働中の
画面が即座に表示される。
"""

from gui import MeetingCostApp

_DEMO_ELAPSED_SEC = 47 * 60 + 23   # 47分23秒
_DEMO_PARTICIPANTS = 10
_DEMO_HOURLY_RATE = 4000
_DEMO_PRESET_NOTE = "「週次MTG（60分）」を適用 ─ 10名 / ¥4,000/h / 想定 60 分"


class MockMeetingCostApp(MeetingCostApp):
    """デモ用の初期状態が設定済みの会議コスト計算機。

    通常の :class:`MeetingCostApp` と完全に同じ UI・動作を保ちつつ、
    起動直後から指定した経過時間・設定値でタイマーが稼働した状態を再現する。
    """

    def __init__(self) -> None:
        super().__init__()
        self._participants.set(_DEMO_PARTICIPANTS)
        self._hourly_rate.set(_DEMO_HOURLY_RATE)
        self._elapsed = _DEMO_ELAPSED_SEC
        self._note_var.set(_DEMO_PRESET_NOTE)
        self.after(100, self._toggle)


if __name__ == "__main__":
    app = MockMeetingCostApp()
    app.mainloop()
