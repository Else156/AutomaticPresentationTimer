"""
自動プレゼンテーションタイマーのメインプログラム
参考サイト：https://murasan-itlab.com/raspberry-pi-pico-w-timer-interrupt/
"""
from machine import Timer
from machine import Pin
import micropython
import time

# GPIOピン
SOLENOID_PIN = 28
RIGHT_BOTTON_PIN = 1
LEFT_BOTTON_PIN = 2
MINUTES_BOTTON_PIN = 3
SECOND_BOTTON_PIN = 4
START_STOP_BOTTON_PIN = 5
RESET_BOTTON_PIN = 6

# GPIOピン設定
SOLENOID = Pin(SOLENOID_PIN,Pin.OUT)
RIGHT_BOTTON = Pin(RIGHT_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)
LEFT_BOTTON = Pin(LEFT_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)
MINUTES_BOTTON = Pin(MINUTES_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)
SECOND_BOTTON = Pin(SECOND_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)
START_STOP_BOTTON = Pin(START_STOP_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)
RESET_BOTTON = Pin(RESET_BOTTON_PIN,Pin.IN,Pin.PULL_DOWN)

# 割り込み処理中の例外を作成するための設定
micropython.alloc_emergency_exception_buf(100)

# 経過時間を格納
elapsed_time = 0.0

# 直前に鳴らしたベルの回数を格納
last_bell_count = 0

"""タイマー時間を設定するフェーズに動作する関数
Args:
    None
Returns:
    None
"""
"""
def set_timer():
    while(1):
        if(RIGHT_BOTTON.value == 1):
            # ディスプレイのカーソルを右にずらすプログラム
        elif(LEFT_BOTTON.value == 1):
            # ディスプレイのカーソルを右にずらすプログラム
        elif(MINUTES_BOTTON.value == 1):
            # 分数を設定するプログラム
        elif(SECOND_BOTTON.value == 1):
            # 秒数を設定するプログラム
        elif(START_STOP_BOTTON.value == 1):
            return
"""        

"""ソレノイドを動かしてベルを鳴らす関数
Args:
    None
Returns:
    None
"""
def ring_the_bell():
    SOLENOID.value(1)
    time.sleep(0.1) # ここが原因で時間測定の処理が止まる場合はほかの方法を考える
    SOLENOID.value(0)

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
    print("debug:" ,elapsed_time)
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
    global elapsed_time,last_bell_count
    timer = Timer()     # タイマーを作成     

    # タイマーを初期化して、周期的にコマンドラインに文字を出力する
    timer.init(mode=Timer.PERIODIC, freq=1, callback=elapsed_timer_cnt)

    while(1):
        # timer_1の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 > elapsed_time and timer_3 > elapsed_time and last_bell_count == 0):
            print("debug:alarm timer_1")
            ring_the_bell()
            last_bell_count += 1
        
        # timer_2の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 <= elapsed_time and timer_3 > elapsed_time and last_bell_count == 1):
            print("debug:alarm timer_2")

            ring_the_bell()
            time.sleep(0.3)
            ring_the_bell()

            last_bell_count += 1
        
        # timer_3の時間が過ぎた場合
        if(timer_1 <= elapsed_time and timer_2 <= elapsed_time and timer_3 <= elapsed_time and last_bell_count == 2):
            print("debug:alarm timer_3")

            ring_the_bell()
            time.sleep(0.3)
            ring_the_bell()
            time.sleep(0.3)
            timer.deinit()

            last_bell_count = 0
            break


# set_timer()

# test用呼び出し
timer(5,10,15)