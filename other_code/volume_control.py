import pyautogui

prev_y = None

def is_palm_open(lm):
    fingers = [
        lm[8].y < lm[6].y,
        lm[12].y < lm[10].y,
        lm[16].y < lm[14].y,
        lm[20].y < lm[18].y
    ]
    return all(fingers)

def handle_volume(lm):
    global prev_y
    wrist_y = lm[0].y
    action_triggered = False
    
    if is_palm_open(lm):
        if prev_y is not None:
            dy = wrist_y - prev_y
            SENSITIVITY = 0.005 

            if dy < -SENSITIVITY:
                # print("動作：音量調大")
                pyautogui.press('volumeup') 
                action_triggered = True
                
            elif dy > SENSITIVITY:
                # print("動作：音量調小")
                pyautogui.press('volumedown')
                action_triggered = True
    
    prev_y = wrist_y
    return action_triggered