//時間
long g_runningTimeMillis;   // 現在時刻
long g_timeLimitMillis = 2000;  // 制限時間


void setup() {
  Serial.begin(9600);
}

void loop() {
  g_runningTimeMillis = millis();   // 現在時刻取得
  Serial.println(g_runningTimeMillis);

  if(g_runningTimeMillis >= g_timeLimitMillis){
    exit(0);
  }
}
