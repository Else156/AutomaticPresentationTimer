# ディスプレイモジュールを使用して文字を表示させるコード
import machine
import ssd1306

# --- 初期設定 ---
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
# 画面サイズ 128x64
display = ssd1306.SSD1306_I2C(128, 64, i2c)


def draw_timer_screen(current_min, current_sec, bell_settings):
    """
    画面を描画する関数
    
    Args:
        current_min (int): 現在の残り分数 (または経過分数)
        current_sec (int): 現在の残り秒数
        bell_settings (list): [1回鳴らす時間, 2回鳴らす時間, 3回鳴らす時間]
                              例: [10, 15, 20] -> 10分, 15分, 20分
    """
    display.fill(0)  # 画面をクリア
    
    # ベル設定の表示
    display.text("1){:2}".format(bell_settings[0]), 0, 0)
    display.text("2){:2}".format(bell_settings[1]), 48, 0)
    display.text("3){:2}".format(bell_settings[2]), 95, 0)

    # 区切り線を描画
    display.hline(0, 10, 128, 1)

    # 現在のタイマー時間 
    time_str = "{:02}:{:02}".format(current_min, current_sec)
    
    # SSD1306の標準フォントは小さい(8x8)ため、視認性を上げるために
    # 文字列を中央(x=44付近)かつ、少し太く見えるよう2重描画する
    display.text(time_str, 44, 25)
    display.text(time_str, 45, 25) # 横に1ピクセルずらして太字風にする

    # 操作説明
    display.text("click: run/stop", 2, 45)
    display.text("hold : menu",    2, 55)

    # 描画を反映
    display.show()

def draw_menu_screen(cursor_index, items):
    """
    設定メニュー画面を描画する
    Args:
        cursor_index (int): 現在選択中のインデックス
        items (list): 表示する文字列のリスト
    """
    display.fill(0)
    display.text("-- SETTING --", 20, 0)
    
    start_y = 12
    line_height = 10
    
    for i, item in enumerate(items):
        y = start_y + (i * line_height)
        prefix = ">" if i == cursor_index else " "
        display.text(f"{prefix} {item}", 0, y)
        
    display.show()

def draw_edit_screen(title, value):
    """
    値編集画面を描画する
    Args:
        title (str): 項目名 (例: "1st Bell")
        value (int): 現在の設定値 (分)
    """
    display.fill(0)
    display.text(f"Edit: {title}", 0, 0)
    display.hline(0, 10, 128, 1)
    
    # 値を中央に大きく表示
    val_str = f"{value} min"
    display.text(val_str, 40, 30)
    display.text(val_str, 41, 30) # 太字風
    
    display.text("Rotate: Change", 0, 45)
    display.text("Click : OK",     0, 53)
    
    display.show()
