# 物理ベル式 プレゼンテーションタイマー 

Raspberry Pi Pico、SSD1306 OLEDディスプレイ、ソレノイド、およびチンベルを使用したプレゼンテーションタイマーです。
設定した時間（例：予鈴、中間鈴、終了鈴）になると、物理的なベルを「チン！」と鳴らして知らせます。
操作にはRGBロータリーエンコーダを使用し、直感的なメニュー操作と時間設定が可能です。

## ✨ 特徴

* **物理ベル鳴動**: ソレノイドを使用し、設定時間にチンベルを鳴らします。
* **3段階のアラーム設定**: 1回目（1回鳴る）、2回目（2回鳴る）、終了時（3回鳴る）の時間を個別に設定可能。
* **直感的なUI**: ロータリーエンコーダを回して選択・数値変更、押し込んで決定。
* **設定保存機能**: 設定した時間は内蔵フラッシュに保存され、電源を切っても保持されます。
* **加速スクロール**: 時間設定時、エンコーダを速く回すと数値が大きく変化する加速処理を搭載。
* **OLEDディスプレイ**: 現在の残り時間、設定状態、操作ガイドを分かりやすく表示。

## 🛠 ハードウェア構成

### 使用部品

| 部品名 | 型番 | URL | 備考 |
| :--- | :--- | :--- | :--- |
| Raspberry Pi Pico | SC0915 | [購入先URL](https://akizukidenshi.com/catalog/g/g116132/) | |
| 有機ELディスプレイ(OLED) 白色 |  | 購入先URL[https://akizukidenshi.com/catalog/g/g112031/]| |
| イルミネーションロータリーエンコーダ用ピッチ変換基板 | SFE-BOB-11722 | 購入先URL[https://www.switch-science.com/products/1308?srsltid=AfmBOopGGrrqZFvyvS5xYhzGZG8HVmHDNQKUY4yKhhwYDoHrCVhfIAhd] | 廃盤だが千石電商では販売(2026年1月時点） |
| ソレノイド | ZHO-0420S-05A4.5(5V) | 購入先URL[https://akizukidenshi.com/catalog/g/g110761//] | |
| NchパワーMOSFET | 2SK4017(Q) | 購入先URL[https://akizukidenshi.com/catalog/g/g107597/] | |
| カーボン抵抗　10kΩ | RD25S 10K | 購入先URL[https://akizukidenshi.com/catalog/g/g125103/] | |
| 汎用整流用ダイオード 1000V1A | 1N4007-B | 購入先URL[https://akizukidenshi.com/catalog/g/g108327/] | |
| 電解コンデンサー1000μF35V | 35ZLH1000MEFC12.5X20 | 購入先URL[https://akizukidenshi.com/catalog/g/g102722/] | |
| チェック端子(テストポイント) | TEST-22 | 購入先URL[https://akizukidenshi.com/catalog/g/g112216/] | |
| チンベル（卓上ベル） |  |  | |


### 🔌 配線 (Pinout)

`hardware.py` のデフォルト設定に基づく配線図です。

| 部品 | ピン名 | Pico GPIO | 備考 |
| :--- | :--- | :--- | :--- |
| **OLED (I2C)** | SDA | GP0 | |
| | SCL | GP1 | |
| | VCC/GND | - | 3.3V / GND |
| **Encoder** | A相 (CLK) | GP10 | Pull-Up設定 |
| | B相 (DT) | GP11 | Pull-Up設定 |
| | Switch (SW)| GP12 | Pull-Up設定 (Active Low) |
| | GND | - | 共通GND |
| **Solenoid** | Gate/Base | GP15 | **要ドライバ回路** |

> [!WARNING]
> **警告**: ソレノイドをGPIOピン(GP15)に直接接続しないでください。過電流と逆起電力によりPicoが破損します。必ずMOSFET等を使用したドライバ回路と、保護用ダイオードを組み込んでください。

## 📂 ファイル構成

プロジェクトは機能ごとにモジュール化されています。

```text
.
├── main.py                   # エントリーポイント。状態遷移と設定の保存/読込を管理
├── hardware.py               # GPIO制御（ソレノイド、エンコーダ、ボタン）
├── display.py                # SSD1306への描画処理
├── presentation_timer_mode.py # タイマー計測・実行モードのロジック
├── setting_mode.py           # メニュー選択モードのロジック
├── edit_mode.py              # 時間設定変更モードのロジック
├── ssd1306.py                # ディスプレイ用ドライバライブラリ (別途入手)
└── settings.json             # 設定保存ファイル (初回実行時に自動生成)
