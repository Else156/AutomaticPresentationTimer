# タイマー機能
# メインプログラムに結合する前の単体テストコード

import machine
import time


def run_timer(target_seconds):
    """タイマーを実行する関数"""
    if target_seconds <= 0:
        print("エラー: 1以上の整数を指定してください。")
        return
    
    try:
        print(f"\n--- {target_seconds}秒タイマー スタート ---")
        start_ticks = time.ticks_ms()
        end_ticks = time.ticks_add(start_ticks, target_seconds * 1000)
        last_display = target_seconds + 1 # 表示更新用の変数

        while True:
            current_ticks = time.ticks_ms()
            diff = time.ticks_diff(end_ticks, current_ticks)
            
            if diff <= 0:
                break
            
            remaining_sec = int(diff / 1000) + 1
            
            # 画面表示がチラつかないように、秒数が変わった瞬間だけprintする
            if remaining_sec < last_display:
                print(f"残り: {remaining_sec}秒")
                last_display = remaining_sec
            
            # CPU負荷を下げるための短い待機（精度には影響しない）
            time.sleep(0.05)

        print("\n残り: 0秒")
        print("!!! 時間です !!!")
        
    except KeyboardInterrupt:
        print("\n中断されました。")
    


# --- プログラム実行 ---
if __name__ == "__main__":
    while True:
        try:
            user_input = input("タイマーの時間を秒単位で入力してください (例: 10) > ")
            seconds = int(user_input)
            run_timer(seconds)
            break # 正常終了でループを抜ける

        except ValueError:
            print("エラー: 数字を入力してください。")
        except KeyboardInterrupt:
            print("\nプログラムを終了します。")
            break
    