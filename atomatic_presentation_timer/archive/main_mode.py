"""
Main Mode (待機・計測画面)
表示: 現在のタイマー時間、設定値の簡易表示（1回:10分, 2回:15分）、操作の説明
操作:
　　短押し：スタート/ストップ
　　長押し：Setting Modeへ遷移
"""
import time
import display

# ---------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------
def min_to_sec(minutes):
    """
    分を受け取り、秒（整数）に変換して返す
    例: 1.5分 -> 90秒
    """
    return int(minutes * 60)


def sec_to_time_list(total_seconds):
    """
    秒数を [分, 秒] のリストに変換する
    例: 90 -> [1, 30]
    """
    minutes = total_seconds // 60  # 分（商）
    seconds = total_seconds % 60   # 秒（余り）
    return [minutes, seconds]

# ---------------------------------------------------------
# メイン実行関数
# ---------------------------------------------------------
def run_timer_and_ring(bell_settings):
    """
    タイマーを実行してベルを鳴らす関数
    
    Args:
        bell_settings (list): [1回鳴らす時間, 2回鳴らす時間, 3回鳴らす時間]
                              例: [10, 15, 20] -> 10分, 15分, 20分
    return:
        None:正常終了時
        int:エラー発生時
            1:target_secondsに0以下の整数が指定されている
    """
    
    target_seconds = min_to_sec(bell_settings[2])
    
    if target_seconds <= 0:
        print("エラー: 1以上の整数を指定してください。")
        return　1
    
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
                min_sec = sec_to_time_list(remaining_sec)
                display.draw_timer_screen(min_sec[0], min_sec[1], bell_settings)
                last_display = remaining_sec
            
            # CPU負荷を下げるための短い待機（精度には影響しない）
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n中断されました。")
    


# --- プログラム実行 ---
if __name__ == "__main__":
    try:
        run_timer_and_ring([1,2,3])

    except ValueError:
        print("エラー: 数字を入力してください。")
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")
    
