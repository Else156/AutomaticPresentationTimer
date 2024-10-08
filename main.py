"""
自動プレゼンテーションタイマーのメインプログラム
参考サイト：https://murasan-itlab.com/raspberry-pi-pico-w-timer-interrupt/
"""
from machine import Timer
import micropython

# 割り込み処理中の例外を作成するための設定
micropython.alloc_emergency_exception_buf(100)

# 経過時間を格納
elapsed_time = 0.0


"""経過時間をカウントする関数
Args:
    timer:
        タイマーオブジェクト
Returns:
    None
"""
def elapsed_timer_cnt(timer):
    global elapsed_time
    elapsed_time += 1
    # TODO:ディスプレイに現在経過時間を出力する関数を呼び出す


"""タイマー機能を制御する関数
Args:
    timer_1:
        int: ベルを1回鳴らす時間
    timer_2:
        int: ベルを2回鳴らす時間
    timer_3:
        int: ベルを3回鳴らす時間
Returns:
    None
"""
def timer(timer_1:int, timer_2:int, timer_3:int):
    global elapsed_time
    timer = Timer()     # タイマーを作成     

    # タイマーを初期化して、周期的にコマンドラインに文字を出力する
    timer.init(mode=Timer.PERIODIC, freq=1, callback=elapsed_timer_cnt)

    while(1):
        # timer_1の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 > elapsed_time and timer_3 > elapsed_time):
            # TODO:ソレノイドを1回鳴らす処理をする
        
        # timer_2の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 <= elapsed_time and timer_3 > elapsed_time):
            # TODO:ソレノイドを2回鳴らす処理をする
        
        # timer_3の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 <= elapsed_time and timer_3 <= elapsed_time):
            # TODO:ソレノイドを3回鳴らす処理をする
            Timer.deinit()
            break
