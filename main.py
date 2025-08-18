# 必要なライブラリをインポート
from machine import Pin, Timer
import time
from lcd import Lcd

# --- グローバル変数と定数設定 ---

# GPIOピン設定
# ソレノイド
SOLENOID_PIN = 28
# ボタン
UP_BUTTON_PIN = 1
DOWN_BUTTON_PIN = 2
INCREASE_BUTTON_PIN = 3
DECREASE_BUTTON_PIN = 4
START_STOP_BUTTON_PIN = 5
RESET_BUTTON_PIN = 6

# パラレルLCDのピン設定
LCD_RS_PIN = 16
LCD_E_PIN = 17
LCD_D4_PIN = 18
LCD_D5_PIN = 19
LCD_D6_PIN = 20
LCD_D7_PIN = 21

# 状態管理のための定数 (変更なし)
STATE_SETTING = 0
STATE_READY = 1
STATE_RUNNING = 2
STATE_PAUSED = 3
STATE_FINISHED = 4

# --- グローバル変数 --- (変更なし)
current_state = STATE_SETTING
elapsed_time = 0
bell_times = [0, 0, 0]
bell_rang_flags = [False, False, False]
setting_cursor_pos = 0
last_button_press_time = 0

# --- ハードウェア初期化 ---
# ソレノイド・ボタン (変更なし)
solenoid = Pin(SOLENOID_PIN, Pin.OUT)
solenoid.value(0)
up_button = Pin(UP_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
down_button = Pin(DOWN_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
increase_button = Pin(INCREASE_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
decrease_button = Pin(DECREASE_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
start_stop_button = Pin(START_STOP_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
reset_button = Pin(RESET_BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)

# ディスプレイの初期化
lcd = Lcd(rs=LCD_RS_PIN, e=LCD_E_PIN, d4=LCD_D4_PIN, d5=LCD_D5_PIN, d6=LCD_D6_PIN, d7=LCD_D7_PIN)
lcd.putstr("Presentation\nTimer Ready!")
time.sleep(2)

# タイマーオブジェクト (変更なし)
timer = Timer()

# --- 関数定義 ---
def debounce():
    global last_button_press_time
    now = time.ticks_ms()
    if time.ticks_diff(now, last_button_press_time) < 200:
        return False
    last_button_press_time = now
    return True

def format_time(seconds):
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def ring_bell(count):
    for _ in range(count):
        solenoid.value(1)
        time.sleep(0.1)
        solenoid.value(0)
        time.sleep(0.3)

def update_setting_display():
    """設定画面をディスプレイに表示する"""
    lcd.clear()
    # 1行目に表示するベル設定
    cursor1 = ">" if setting_cursor_pos == 0 else " "
    lcd.move_to(0, 0)
    lcd.putstr(f"{cursor1}Bell 1: {format_time(bell_times[0])}")
    
    # 2行目に表示するベル設定
    cursor2 = ">" if setting_cursor_pos == 1 else " "
    lcd.move_to(0, 1)
    lcd.putstr(f"{cursor2}Bell 2: {format_time(bell_times[1])}")

    # 3つ目の設定はカーソルが来たときだけ表示を切り替える
    if setting_cursor_pos == 2:
        cursor3 = ">"
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f" Bell 2: {format_time(bell_times[1])}") # 前の設定を上段に
        lcd.move_to(0, 1)
        lcd.putstr(f"{cursor3}Bell 3: {format_time(bell_times[2])}")

def tick(t):
    global elapsed_time
    elapsed_time += 1
    update_timer_display()

def update_timer_display():
    lcd.clear()
    lcd.putstr(f"Time: {format_time(elapsed_time)}")
    next_bell_time = -1
    next_bell_num = 0
    sorted_times = sorted([(t, i+1) for i, t in enumerate(bell_times) if t > 0])
    for t, num in sorted_times:
        if t > elapsed_time:
            next_bell_time = t
            next_bell_num = num
            break
    if next_bell_time != -1:
        lcd.move_to(0, 1)
        lcd.putstr(f"Next: B{next_bell_num} {format_time(next_bell_time)}")
    else:
        lcd.move_to(0, 1)
        lcd.putstr("All bells rang.")

def reset_timer():
    global elapsed_time, current_state, bell_rang_flags
    timer.deinit()
    elapsed_time = 0
    bell_rang_flags = [False, False, False]
    current_state = STATE_SETTING
    update_setting_display()

# --- メインループ ---
def main():
    global current_state, setting_cursor_pos, bell_times
    
    update_setting_display()

    while True:
        if current_state == STATE_SETTING:
            if up_button.value() and debounce():
                setting_cursor_pos = (setting_cursor_pos - 1 + 3) % 3
                update_setting_display()
            
            if down_button.value() and debounce():
                setting_cursor_pos = (setting_cursor_pos + 1) % 3
                update_setting_display()

            if increase_button.value(): # 増加は長押しを考慮してdebounceを外す
                bell_times[setting_cursor_pos] += 1
                update_setting_display()
                time.sleep(0.1) # 連続増加のスピード調整
                
            if decrease_button.value(): # 減少も同様
                if bell_times[setting_cursor_pos] > 0:
                    bell_times[setting_cursor_pos] -= 1
                    update_setting_display()
                time.sleep(0.1)

            if start_stop_button.value() and debounce():
                if any(t > 0 for t in bell_times):
                    current_state = STATE_READY
                    lcd.clear()
                    lcd.putstr("Ready to Start\nPress S/S button")
        
        elif current_state in [STATE_READY, STATE_PAUSED]:
            if start_stop_button.value() and debounce():
                current_state = STATE_RUNNING
                timer.init(freq=1, mode=Timer.PERIODIC, callback=tick)
                update_timer_display()
            
            if reset_button.value() and debounce():
                reset_timer()

        elif current_state == STATE_RUNNING:
            for i in range(3):
                if bell_times[i] > 0 and not bell_rang_flags[i] and elapsed_time >= bell_times[i]:
                    ring_bell(i + 1)
                    bell_rang_flags[i] = True
            
            if all(flag or time == 0 for flag, time in zip(bell_rang_flags, bell_times)):
                current_state = STATE_FINISHED
                timer.deinit()
                lcd.move_to(0, 1)
                lcd.putstr("Finished!       ")

            if start_stop_button.value() and debounce():
                current_state = STATE_PAUSED
                timer.deinit()
                lcd.move_to(0, 1)
                lcd.putstr("PAUSED          ")

            if reset_button.value() and debounce():
                reset_timer()
        
        elif current_state == STATE_FINISHED:
            if reset_button.value() and debounce():
                reset_timer()

        time.sleep(0.01)

if __name__ == "__main__":
    main()