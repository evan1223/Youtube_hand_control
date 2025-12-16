import pyautogui
import time

prev_x = None
prev_time = 0

def handle_swipe(lm, handedness, cooldown_state):
    global prev_x, prev_time
    
    current_time = time.time()
    wrist_x = lm[0].x
    
    SWIPE_THRESHOLD = 0.04
    COOLDOWN = 1.0 

    # 冷卻中，回傳 False
    if current_time - cooldown_state.get('swipe', 0) < COOLDOWN:
        prev_x = wrist_x
        prev_time = current_time
        return False

    action_triggered = False

    if prev_x is not None:
        dx = wrist_x - prev_x
        dt = current_time - prev_time
        if dt == 0: dt = 0.001
        
        if handedness == "Right" and dx < -SWIPE_THRESHOLD:
            print("動作：下一部影片 (Shift+N)")
            pyautogui.hotkey('shift', 'n')
            cooldown_state['swipe'] = current_time
            action_triggered = True
            
        elif handedness == "Left" and dx > SWIPE_THRESHOLD:
            print("動作：上一部影片 (Shift+P)")
            pyautogui.hotkey('shift', 'p')
            cooldown_state['swipe'] = current_time
            action_triggered = True

    prev_x = wrist_x
    prev_time = current_time
    return action_triggered