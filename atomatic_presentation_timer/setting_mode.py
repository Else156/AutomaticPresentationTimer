import time
import hardware
import display

class SettingMode:
    def __init__(self, hardware_interface):
        self.hw = hardware_interface
        # メニュー項目
        self.items = [
            "1st Bell (1)",
            "2nd Bell (2)",
            "3rd Bell (3)",
            "START TIMER"
        ]
        self.cursor_index = 0

    def run(self):
        """
        メニュー画面ループ
        Return:
            int: 選択されたアクションコード
                 0-2: 設定項目のインデックス (編集へ)
                 3:   タイマースタート
        """
        print("--- Setting Mode ---")
        
        # 画面初回描画
        display.draw_menu_screen(self.cursor_index, self.items)
        time.sleep(0.2) # 遷移直後の誤操作防止

        while True:
            # 1. 回転入力 (カーソル移動)
            delta = self.hw.get_rotation_delta()
            if delta != 0:
                # 項目数でループさせる
                self.cursor_index = (self.cursor_index + delta) % len(self.items)
                display.draw_menu_screen(self.cursor_index, self.items)
                print(f"Cursor: {self.cursor_index}")

            # 2. ボタン入力 (決定)
            event = self.hw.get_button_event()
            if event == "SHORT_PRESS":
                print(f"Selected: {self.items[self.cursor_index]}")
                return self.cursor_index

            time.sleep(0.05)
            
if __name__ == "__main__":
    print("=== Setting Mode Test Start ===")
    print("エンコーダを回して項目選択、ボタンで決定してください。")
    print("Ctrl+C で終了します。")

    try:
        hw = hardware.HardwareInterface()
    except Exception as e:
        print(f"ハードウェア初期化エラー: {e}")

    app = SettingMode(hw)

    try:
        while True:
            print("\n--- メニュー待機中 ---")
            
            # ユーザーがボタンを押すまでここで処理がブロックされます
            selected_index = app.run()
            
            # 結果の表示
            if selected_index == 3:
                print(f"結果: [START TIMER] が選択されました (Index: {selected_index})")
            else:
                print(f"結果: 設定項目 [{selected_index}] が選択されました")
            
            # すぐに再ループするとチャタリングで誤作動しやすいので少し待つ
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nテストを終了します。")