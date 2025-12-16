# config.py

# --- 動作冷卻時間 ---
COOLDOWN_TIME = 1.0     # 切換影片的冷卻時間
MUTE_HOLD_TIME = 2.5    # 靜音觸發時間

# --- 判定參數 ---
SWIPE_THRESHOLD = 20    # 切換影片的滑動門檻
STILL_THRESHOLD = 3     # 靜音防手抖門檻

# [新] 音量觸發界線 (像素)
# 當大拇指與食指距離...
# 1. 大於這個數值 -> 持續變大聲 (建議 130~160)
DIST_MAX_TRIGGER = 140  

# 2. 小於這個數值 -> 持續變小聲 (建議 30~50)
DIST_MIN_TRIGGER = 40   

# (介於 40 ~ 140 中間時，音量不會變，這是休息區)

# --- 攝影機設定 ---
CAM_WIDTH = 640
CAM_HEIGHT = 480

# --- 按鍵對應 ---
KEY_PREV = ['shift', 'p']
KEY_NEXT = ['shift', 'n']
KEY_VOL_UP = 'up'       
KEY_VOL_DOWN = 'down'   
KEY_MUTE = 'm'