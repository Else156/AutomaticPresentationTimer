import time
import json
import machine

# 自作モジュール
import hardware
import display
from presentation_timer_mode import PresentationTimerMode, TimerStatus
from setting_mode import SettingMode
from edit_mode import EditMode

# --- 設定ファイル管理 ---
SETTINGS_FILE = "settings.json"

def load_settings():
    """設定をJSONから読み込む。なければデフォルト値を返す"""
    default_settings = [7, 10, 15] # 単位は「分」
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            print("設定をロードしました:", data)
            return data
    except (OSError, ValueError):
        print("設定ファイルが見つかりません。デフォルトを使用します。")
        return default_settings

def save_settings(settings):
    """設定をJSONに保存する"""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
            print("設定を保存しました:", settings)
    except OSError as e:
        print("保存エラー:", e)

# --- メインループ ---
def main():
    # 1. ハードウェア初期化
    hw = hardware.HardwareInterface()
    
    # 2. モードインスタンス生成
    timer_mode = PresentationTimerMode(hw)
    setting_mode = SettingMode(hw)
    edit_mode = EditMode(hw)
    
    # 3. 設定ロード
    bell_settings = load_settings()
    
    # 状態管理定数
    STATE_MENU = 0
    STATE_EDIT = 1
    STATE_TIMER = 2
    
    current_state = STATE_MENU
    selected_edit_index = 0 # どの時間を編集しているか (0-2)

    print("システム起動")

    while True:
        if current_state == STATE_MENU:
            # --- Setting Mode ---
            action = setting_mode.run()
            
            if action == 3: # "START TIMER" が選ばれた
                current_state = STATE_TIMER
            else:           # 設定項目(0, 1, 2)が選ばれた
                selected_edit_index = action
                current_state = STATE_EDIT

        elif current_state == STATE_EDIT:
            # --- Edit Mode ---
            # 編集する項目のタイトルを決める
            titles = ["1st Bell", "2nd Bell", "3rd Bell"]
            current_title = titles[selected_edit_index]
            current_val = bell_settings[selected_edit_index]
            
            # 編集モード実行 -> 新しい値を受け取る
            new_val = edit_mode.run(current_title, current_val)
            
            # 値を更新して保存
            bell_settings[selected_edit_index] = new_val
            save_settings(bell_settings)
            
            # メニューに戻る
            current_state = STATE_MENU

        elif current_state == STATE_TIMER:
            # --- Presentation Timer Mode ---
            # タイマー実行 (ブロック処理)
            result = timer_mode.run(bell_settings)
            
            # タイマー終了後、または長押し中断後の処理
            if result == TimerStatus.GO_TO_SETTINGS or result == TimerStatus.FINISHED:
                current_state = STATE_MENU
            
            # エラー等の場合もとりあえずメニューへ
            else:
                current_state = STATE_MENU

        # CPU休憩 (モード遷移の間)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
