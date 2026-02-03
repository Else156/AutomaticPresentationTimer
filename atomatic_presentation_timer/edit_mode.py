import time
import hardware
import display


class EditMode:
    def __init__(self, hardware_interface):
        self.hw = hardware_interface

    def run(self, title, current_value):
        """
        値編集ループ
        Args:
            title (str): 画面に表示する項目名
            current_value (int): 現在の設定値
        Return:
            int: 変更後の設定値
        """
        print(f"--- Edit Mode: {title} ---")
        value = current_value
        
        # 画面初回描画
        display.draw_edit_screen(title, value)
        time.sleep(0.2)

        while True:
            # 1. 回転入力 (値の増減)
            delta = self.hw.get_rotation_delta()
            if delta != 0:
                # 加速処理: ハードウェア側で回転カウントが溜まっている(=速く回した)場合、
                # そのまま加算することで自然と大きな変化になります。
                # さらに強調したい場合は以下のように倍率をかけます。
                if abs(delta) > 2:
                    change = delta * 2 # 速く回したら変化量を2倍に
                else:
                    change = delta
                
                value += change
                
                # 範囲制限 (例: 1分〜180分)
                if value < 1: value = 1
                if value > 180: value = 180
                
                display.draw_edit_screen(title, value)
                print(f"Value: {value}")

            # 2. ボタン入力 (決定・保存)
            event = self.hw.get_button_event()
            if event == "SHORT_PRESS":
                print(f"Saved: {value}")
                return value

            time.sleep(0.05)

if __name__ == "__main__":
    print("=== Edit Mode Test Start ===")
    print("エンコーダを回して数値変更、ボタンで決定してください。")
    print("Ctrl+C で終了します。")

    try:
        hw = hardware.HardwareInterface()
    except Exception as e:
        print(f"ハードウェア初期化エラー: {e}")

    app = EditMode(hw)

    # テスト用の初期値
    test_value = 10 
    test_title = "Test Item"

    try:
        while True:
            print(f"\n--- 編集モード起動 (現在の値: {test_value}) ---")
            new_value = app.run(test_title, test_value)
            
            print(f"決定されました。")
            print(f"変更前: {test_value} -> 変更後: {new_value}")
            
            test_value = new_value
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nテストを終了します。")