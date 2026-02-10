"""
Presentation Timer Mode (待機・計測画面)
表示: 現在のタイマー時間、設定値の簡易表示（1回:10分, 2回:15分）、操作の説明
操作:
　　短押し：スタート/ストップ
　　長押し：Setting Modeへ遷移
"""

import time
import display
import hardware

class TimerStatus:
    """上位コードへ返すステータス定数"""
    FINISHED = 0       # タイマー正常終了
    GO_TO_SETTINGS = 1 # 設定画面へ遷移リクエスト
    ERROR = -1         # エラー発生

class PresentationTimerMode:
    def __init__(self, hardware_interface):
        """
        Args:
            hardware_interface: ボタン入力やベル鳴動を行うハードウェア管理クラス
                                (get_button_event, ring_bell などのメソッドを持つ想定)
        """
        self.hw = hardware_interface
        self.is_paused = False

    def _min_to_sec(self, minutes):
        return int(minutes * 60)

    def _sec_to_min_sec(self, total_seconds):
        return total_seconds // 60, total_seconds % 60

    def _check_and_ring_bell(self, current_remaining_sec, total_duration_sec, bell_settings):
        """
        残り時間に応じてベルを鳴らす
        ここでのロジック例:
          残り時間が「設定値に対応する経過時間」と一致したら鳴らす
        """
        elapsed_sec = total_duration_sec - current_remaining_sec

        # 設定: [1回鳴らす時間(分), 2回鳴らす時間(分), 3回鳴らす時間(分)]
        # 秒に変換して比較
        times_to_ring = 0
        
        # 厳密な一致判定 (ループ周期によっては <= などで範囲判定が必要な場合もあり)
        if elapsed_sec == self._min_to_sec(bell_settings[0]):
            times_to_ring = 1
        elif elapsed_sec == self._min_to_sec(bell_settings[1]):
            times_to_ring = 2
        elif elapsed_sec == self._min_to_sec(bell_settings[2]):
            times_to_ring = 3
        
        if times_to_ring > 0:
            self.hw.ring_bell(times_to_ring) 

    def run(self, bell_settings):
        """
        タイマーメインループ
        上位コードからはこのメソッドを呼ぶだけでモードが実行される
        """
        # 1. 初期設定とガード節
        # bell_settingsの3番目(インデックス2)を終了時間とする
        total_duration_sec = self._min_to_sec(bell_settings[2])
        
        if total_duration_sec <= 0:
            print("エラー: 設定値が不正です")
            return TimerStatus.ERROR

        # 2. タイマー開始準備
        print(f"--- {total_duration_sec}秒タイマー スタート ---")
        start_ticks = time.ticks_ms()
        # 終了予定時刻を計算
        end_ticks = time.ticks_add(start_ticks, total_duration_sec * 1000)
        
        last_displayed_sec = -1
        
        # 3. メインループ
        try:
            while True:
                # --- A. ボタン入力の処理 (割り込み/ポーリング) ---
                # ハードウェア側で判定されたイベントを取得
                event = self.hw.get_button_event() 

                if event == "LONG_PRESS":
                    print("長押し検出: 設定モードへ遷移します")
                    return TimerStatus.GO_TO_SETTINGS
                
                elif event == "SHORT_PRESS":
                    self.is_paused = not self.is_paused
                    print("一時停止" if self.is_paused else "再開")
                    # ※ポーズ実装時は start_ticks のずらし処理などが別途必要ですが、
                    # ここでは簡易的にループをスキップするだけに留めます
                
                if self.is_paused:
                    time.sleep(0.1)
                    # ポーズ中も終了予定時刻が後ろにズレるように
                    # end_ticks を加算する処理を入れるのが一般的
                    end_ticks = time.ticks_add(end_ticks, 100) 
                    continue

                # --- B. 残り時間の計算 ---
                current_ticks = time.ticks_ms()
                remaining_ms = time.ticks_diff(end_ticks, current_ticks)
                
                # 終了判定
                if remaining_ms <= 0:
                    print("タイマー終了")
                    # 終了時のベル（3回）を強制的に鳴らすならここで呼ぶ
                    self.hw.ring_bell(3)
                    display.draw_timer_screen(0, 0, bell_settings)
                    return TimerStatus.FINISHED

                # ミリ秒 -> 秒 (切り上げ表示が見やすい)
                remaining_sec = (remaining_ms // 1000) + 1

                # --- C. 画面更新とベル制御 (1秒に1回だけ実行) ---
                if remaining_sec != last_displayed_sec:
                    
                    # 画面表示
                    m, s = self._sec_to_min_sec(remaining_sec)
                    print(f"残り: {m:02}:{s:02}")
                    display.draw_timer_screen(m, s, bell_settings)
                    
                    # ベル判定
                    self._check_and_ring_bell(remaining_sec, total_duration_sec, bell_settings)

                    last_displayed_sec = remaining_sec

                # --- D. CPU負荷軽減 ---
                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n強制中断")
            return TimerStatus.ERROR

# --- ダミーのハードウェアクラス (テスト用) ---
class MockHardware:
    def get_button_event(self):
        # ここに実際のGPIO判定ロジックを入れる
        # 戻り値: None, "SHORT_PRESS", "LONG_PRESS"
        return None
    
    def ring_bell(self, times):
        print(f"カチカチ... ({times}回)")

# --- 上位コード (Main Program) からの呼び出しイメージ ---
if __name__ == "__main__":
    hw = hardware.HardwareInterface()
    timer_mode = PresentationTimerMode(hw)
    
    # 設定値 (1分, 2分, 30分)
    settings = [1, 2, 3]
    status = timer_mode.run(settings)
    
    if status == TimerStatus.GO_TO_SETTINGS:
        print(">> 設定画面へ切り替えます")
    elif status == TimerStatus.FINISHED:
        print(">> タイマーが完了しました")