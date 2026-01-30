import machine
import time

class HardwareInterface:
    """
    ハードウェア（GPIO）を管理するクラス
    ソレノイドの駆動と、ボタンのイベント検出を行う
    """

    # 定数定義
    SOLENOID_PIN_NUM = 15   # ソレノイド用
    BUTTON_PIN_NUM = 14     # ボタン用（配線に合わせて変更してください）
    
    # 時間設定 (ミリ秒)
    SOLENOID_ON_MS = 60     # ソレノイドを通電する時間（打撃の強さ）
    SOLENOID_INTERVAL_MS = 250 # 連続で鳴らす際の間隔
    
    LONG_PRESS_MS = 800     # 長押しと判定する閾値
    DEBOUNCE_MS = 50        # チャタリング防止用の最短時間

    def __init__(self):
        # ソレノイドの初期化 (出力)
        self.solenoid = machine.Pin(self.SOLENOID_PIN_NUM, machine.Pin.OUT)
        self.solenoid.value(0) # 初期状態はOFF

        # ボタンの初期化 (入力, プルダウン抵抗)
        # ※ボタンを押すと3.3Vが入力される配線を想定
        self.button = machine.Pin(self.BUTTON_PIN_NUM, machine.Pin.IN, machine.Pin.PULL_DOWN)

        # ボタン状態管理用変数
        self.last_press_start = 0
        self.is_pressing = False
        self.long_press_triggered = False

    def ring_bell(self, times):
        """
        指定された回数だけベル（ソレノイド）を鳴らす
        Args:
            times (int): 鳴らす回数
        """
        print(f"[Hardware] ベルを{times}回鳴らします")
        
        for i in range(times):
            # ON: ソレノイドを引き込む（叩く）
            self.solenoid.value(1)
            time.sleep_ms(self.SOLENOID_ON_MS)
            
            # OFF: 元に戻す
            self.solenoid.value(0)
            
            # 最後の1回以外は、次の打撃までの間隔を空ける
            if i < times - 1:
                time.sleep_ms(self.SOLENOID_INTERVAL_MS)

    def get_button_event(self):
        """
        ボタンの状態を確認し、イベントがあれば返す
        メインループから繰り返し呼び出されることを想定
        
        Return:
            "SHORT_PRESS": 短押しして離した
            "LONG_PRESS" : 長押し（押している最中に検知）
            None         : イベントなし
        """
        current_time = time.ticks_ms()
        is_pin_high = (self.button.value() == 1)
        event = None

        if is_pin_high:
            if not self.is_pressing:
                # --- 押し始め ---
                self.is_pressing = True
                self.long_press_triggered = False
                self.last_press_start = current_time
            else:
                # --- 押している最中 ---
                # 既に長押し時間を超えていて、かつまだイベントを発火していない場合
                duration = time.ticks_diff(current_time, self.last_press_start)
                if duration > self.LONG_PRESS_MS and not self.long_press_triggered:
                    self.long_press_triggered = True
                    event = "LONG_PRESS"
        
        else: # ボタンが離されている状態
            if self.is_pressing:
                # --- 離した瞬間 (立ち下がり) ---
                self.is_pressing = False
                duration = time.ticks_diff(current_time, self.last_press_start)
                
                # 長押し済みでなく、かつチャタリング(ごく短時間のノイズ)でない場合
                if not self.long_press_triggered and duration > self.DEBOUNCE_MS:
                    event = "SHORT_PRESS"

        return event

# --- 単体テスト用 ---
if __name__ == "__main__":
    hw = HardwareInterface()
    print("ハードウェアテスト開始: ボタンを押してください...")
    
    try:
        while True:
            evt = hw.get_button_event()
            if evt:
                print(f"検知イベント: {evt}")
                if evt == "SHORT_PRESS":
                    hw.ring_bell(1)
                elif evt == "LONG_PRESS":
                    hw.ring_bell(2)
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("終了")