// 自動プレゼンテーションタイマー用プログラム
#include time;
unsigned long now;

void setup(){
  Serial.begin(9600);
}

void loop(){
  now = millis();
  Serial.println(now);
  time.sleep(1);
}