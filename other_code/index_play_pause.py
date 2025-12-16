import math
import pyautogui

def is_index_toward_camera(lm, xy_thresh=0.01):
    tip = lm[8]
    dip = lm[7]
    dist_xy = math.hypot(tip.x - dip.x, tip.y - dip.y)
    return dist_xy < xy_thresh 

def handle_index_play_pause(lm):
    if is_index_toward_camera(lm):
        pyautogui.press("k")
        print("⏯ 播放/暫停")
        return True # 執行了動作
    return False