import math
import time
import pyautogui

_base_dist = None
_last_action = 0

def get_dist(p1, p2):
    """計算兩點間的歐幾里得距離"""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def is_finger_bent(lm, tip_idx, mcp_idx, thresh=0.12):
    """
    判斷手指是否彎曲
    邏輯：檢查 指尖(Tip) 與 指根(MCP) 的距離是否夠近
    thresh: 門檻值，依據手掌大小可能需微調 (0.1 ~ 0.15)
    """
    dist = get_dist(lm[tip_idx], lm[mcp_idx])
    return dist < thresh

def handle_zoom(lm, pose, cooldown=0.5, up_ratio=1.3, down_ratio=0.75):
    """
    縮放控制
    觸發條件：
    1. 中指、無名指、小拇指 必須彎曲 (避免誤觸)
    2. 根據 大拇指(4) 與 食指(8) 的距離變化來觸發
    """
    global _base_dist, _last_action

    # 1. 檢查三根手指是否彎曲 (中指12-9, 無名指16-13, 小指20-17)
    middle_bent = is_finger_bent(lm, 12, 9)
    ring_bent   = is_finger_bent(lm, 16, 13)
    pinky_bent  = is_finger_bent(lm, 20, 17)

    # 如果有任何一根手指沒彎曲，就不是正確的 Zoom 手勢
    if not (middle_bent and ring_bent and pinky_bent):
        _base_dist = None # 重置基準，避免誤用之前的距離
        return False

    # 2. 計算大拇指與食指距離
    dist = get_dist(lm[4], lm[8])

    # 如果是剛開始偵測到這個手勢，設定為基準距離
    if _base_dist is None:
        _base_dist = dist
        return False

    # 3. 計算變化比例
    ratio = dist / _base_dist
    now = time.time()
    action_triggered = False

    # 4. 判斷縮放 (增加冷卻時間檢查)
    if now - _last_action > cooldown:
        if ratio > up_ratio:
            pyautogui.press("f") # 全螢幕 / 退出全螢幕
            print(f"🔍 ZOOM 動作 (比例: {ratio:.2f})")
            _last_action = now
            action_triggered = True
            # 觸發後重置基準，讓使用者可以連續操作 (如果不希望鎖定太快，這裡可以根據體驗調整)
            # _base_dist = dist 
            
        elif ratio < down_ratio:
            pyautogui.press("f")
            print(f"🔍 ZOOM 動作 (比例: {ratio:.2f})")
            _last_action = now
            action_triggered = True
            # _base_dist = dist

    return action_triggered