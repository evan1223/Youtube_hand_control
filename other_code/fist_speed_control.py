import time
import pyautogui

_fist_start = None
_speed_mode = False

def is_fist(lm, thresh=0.1):
    finger_pairs = [(8,5), (12,9), (16,13), (20,17)]
    for tip, mcp in finger_pairs:
        dx = abs(lm[tip].x - lm[mcp].x)
        dy = abs(lm[tip].y - lm[mcp].y)
        dist = (dx**2 + dy**2) ** 0.5
        if dist > thresh:
            return False
    return True

def handle_fist_speed(lm, hold_time=1.6):
    global _fist_start, _speed_mode
    now = time.time()
    action_finished = False # 用來標記動作是否"完成"並可以鎖定

    if is_fist(lm):
        if _fist_start is None:
            _fist_start = now
        elif not _speed_mode and (now - _fist_start) > hold_time:
            pyautogui.press(">")
            print("⚡ 倍速 ON")
            _speed_mode = True
            # 倍速開啟中，不回傳 True，保持解鎖狀態以偵測放開
    else:
        if _speed_mode and _fist_start is not None:
            pyautogui.press("<")
            print("🐢 倍速 OFF")
            _speed_mode = False
            action_finished = True # 動作結束，可以鎖定了
        _fist_start = None
        
    return action_finished