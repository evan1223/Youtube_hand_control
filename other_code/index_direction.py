import math
import pyautogui

def finger_direction_left_right(lm, thresh=0.03):
    base = lm[5]
    tip  = lm[8]
    dx = tip.x - base.x
    if dx > thresh:
        return "RIGHT"
    elif dx < -thresh:
        return "LEFT"
    else:
        return None

def handle_index_direction(lm, pose):
    if pose != "POINT":
        return False

    direction = finger_direction_left_right(lm)
    action_triggered = False

    if direction == "RIGHT":
        pyautogui.press("right")
        print("➡▶ 快進 5 秒")
        action_triggered = True

    elif direction == "LEFT":
        pyautogui.press("left")
        print("⬅◀ 後退 5 秒")
        action_triggered = True
        
    return action_triggered