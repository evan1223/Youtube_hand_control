import pyautogui
import time

mute_start_time = None
mute_triggered = False

def is_palm_facing(lm):
    fingers_extended = [
        lm[4].x < lm[3].x if lm[17].x < lm[5].x else lm[4].x > lm[3].x,
        lm[8].y < lm[6].y,
        lm[12].y < lm[10].y,
        lm[16].y < lm[14].y,
        lm[20].y < lm[18].y
    ]
    return all(fingers_extended)

def handle_mute(lm):
    global mute_start_time, mute_triggered
    
    current_time = time.time()
    action_triggered = False
    
    if is_palm_facing(lm):
        if mute_start_time is None:
            mute_start_time = current_time
        
        elapsed = current_time - mute_start_time
        
        if elapsed > 2.0 and not mute_triggered:
            print(f"動作：靜音切換")
            pyautogui.press('m')
            mute_triggered = True
            action_triggered = True
    else:
        mute_start_time = None
        mute_triggered = False
        
    return action_triggered