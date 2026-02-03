import machine
import time

class HardwareInterface:
    """
    ハードウェア（GPIO）を管理するクラス
    - ソレノイドの駆動
    - RGBロータリーエンコーダの回転検知
    - エンコーダ内蔵ボタンのイベント検知
    """

    # --- ピン定義 (配線に合わせて変更してください) ---
    SOLENOID_PIN_NUM = 15   # ソレノイド
    
    # ロータリーエンコーダ用ピン
    ENC_A_PIN_NUM = 10      # 回転検知 A相 (CLK)
    ENC_B_PIN_NUM = 11      # 回転検知 B相 (DT)
    BUTTON_PIN_NUM = 12     # スイッチ (SW)

    # --- 設定値 ---
    SOLENOID_ON_MS = 60        # ソレノイド通電時間
    SOLENOID_INTERVAL_MS = 250 # 連打間隔
    
    LONG_PRESS_MS = 800     # 長押し閾値
    DEBOUNCE_MS = 50        # ボタンのチャタリング防止
    
    STEPS_PER_CLICK = 4     # ソレノイドの分解能(1クリックで内部カウンタがいくつ進むか)
    
    def __init__(self):
        # 1. ソレノイド初期化
        self.solenoid = machine.Pin(self.SOLENOID_PIN_NUM, machine.Pin.OUT)
        self.solenoid.value(0) 

        # 2. エンコーダ回転用ピン初期化 (PullUp推奨)
        self.enc_a = machine.Pin(self.ENC_A_PIN_NUM, machine.Pin.IN, machine.Pin.PULL_UP)
        self.enc_b = machine.Pin(self.ENC_B_PIN_NUM, machine.Pin.IN, machine.Pin.PULL_UP)
        
        # 回転量保持用変数（端数もここに溜まり続ける）
        self._rotation_counter = 0
        
        # 割り込み設定 (A相の値が変わった瞬間に _rotary_handler を実行)
        self.enc_a.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self._rotary_handler)
        self.enc_b.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self._rotary_handler)
        self.last_encoded = (self.enc_a.value() << 1) | self.enc_b.value()

        # 3. ボタン初期化 (ロータリーエンコーダはコモンアノードデバイスのためPULL_DOWNに設定)
        self.button = machine.Pin(self.BUTTON_PIN_NUM, machine.Pin.IN, machine.Pin.PULL_DOWN)

        # ボタン状態管理用変数
        self.last_press_start = 0
        self.is_pressing = False
        self.long_press_triggered = False

    def _rotary_handler(self, pin):
        """
        回転検知用の割り込みハンドラ
        (ユーザーが直接呼ぶものではありません)
        """
        # 現在の状態を読み取る
        MSB = self.enc_a.value() # MSB = most significant bit
        LSB = self.enc_b.value() # LSB = least significant bit
        
        encoded = (MSB << 1) | LSB
        sum_val = (self.last_encoded << 2) | encoded
        
        # 状態遷移テーブルのようなロジックで回転方向を判定
        # (一般的なエンコーダの遷移パターン: 0b1101, 0b0100, 0b0010, 0b1011 が1方向)
        if sum_val == 0b1101 or sum_val == 0b0100 or sum_val == 0b0010 or sum_val == 0b1011:
            self._rotation_counter += 1
        elif sum_val == 0b1110 or sum_val == 0b0111 or sum_val == 0b0001 or sum_val == 0b1000:
            self._rotation_counter -= 1
            
        self.last_encoded = encoded

    def get_rotation_delta(self):
        """
        前回のチェック以降の「クリック数」を取得する
        """
        # 必要なステップ数（例:4）に達しているかチェック
        # int()キャストを使うことで、0方向への切り捨てを行う（例: 3/4=0, -3/4=0）
        clicks = int(self._rotation_counter / self.STEPS_PER_CLICK)

        if clicks != 0:
            # 確定したクリック分だけカウンタから減算する
            # 例: counterが5なら、1クリック返して、counterは1残る
            self._rotation_counter -= (clicks * self.STEPS_PER_CLICK)
            return clicks
        
        return 0

    def ring_bell(self, times):
        """指定回数ベルを鳴らす"""
        print(f"[Hardware] ベルを{times}回鳴らします")
        for i in range(times):
            self.solenoid.value(1)
            time.sleep_ms(self.SOLENOID_ON_MS)
            self.solenoid.value(0)
            if i < times - 1:
                time.sleep_ms(self.SOLENOID_INTERVAL_MS)

    def get_button_event(self):
        """
        ボタンイベントの検出 (Active Low対応版)
        Return: "SHORT_PRESS", "LONG_PRESS", None
        """
        current_time = time.ticks_ms()
        
        # ロータリーエンコーダのスイッチは押すとLOW(0)になるため論理を反転
        is_pressed = (self.button.value() == 1)
        
        event = None

        if is_pressed:
            if not self.is_pressing:
                # --- 押し始め ---
                self.is_pressing = True
                self.long_press_triggered = False
                self.last_press_start = current_time
            else:
                # --- 押している最中 ---
                duration = time.ticks_diff(current_time, self.last_press_start)
                if duration > self.LONG_PRESS_MS and not self.long_press_triggered:
                    self.long_press_triggered = True
                    event = "LONG_PRESS"
        
        else: # ボタンが離されている状態
            if self.is_pressing:
                # --- 離した瞬間 ---
                self.is_pressing = False
                duration = time.ticks_diff(current_time, self.last_press_start)
                
                if not self.long_press_triggered and duration > self.DEBOUNCE_MS:
                    event = "SHORT_PRESS"

        return event

# --- 動作確認テスト ---
if __name__ == "__main__":
    hw = HardwareInterface()
    print("ハードウェアテスト開始: エンコーダを回すか押してください...")
    
    try:
        while True:
            # 1. 回転のチェック
            delta = hw.get_rotation_delta()
            if delta != 0:
                # エンコーダの精度によっては 2や4ずつ進むことがあるので適宜割る
                # 例: 実際の1クリックで値が2増えるなら delta // 2 を使う
                direction = "右(CW)" if delta > 0 else "左(CCW)"
                print(f"回転検知: {direction} カウント:{delta}")

            # 2. ボタンのチェック
            evt = hw.get_button_event()
            if evt:
                print(f"ボタン検知: {evt}")
                if evt == "SHORT_PRESS":
                    hw.ring_bell(1)
                elif evt == "LONG_PRESS":
                    hw.ring_bell(2)
            
            time.sleep(0.01) # CPU負荷軽減
            
    except KeyboardInterrupt:
        print("終了")