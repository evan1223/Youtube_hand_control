import cv2
import mediapipe as mp
import pyautogui
import time
from collections import deque
from index_direction import handle_index_direction
from index_play_pause import handle_index_play_pause
from zoom_inout import handle_zoom
from fist_speed_control import handle_fist_speed
from meidas_touch import is_meidas_touch

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)
prev_gesture = None
cooldown = 1.0
last_time = time.time()
unlock = False
available_time = 2.0
set_time = time.time()

def finger_extended(lm, tip, pip, thresh=0.1):
    """手指是否伸出，不看方向，只看距離"""
    # print(lm[tip].x, lm[pip].x, lm[tip].y, lm[pip].y)
    return abs(lm[tip].x - lm[pip].x) > thresh or abs(lm[tip].y - lm[pip].y) > thresh

def classify_static_pose(lm):
    up = [
        finger_extended(lm, 4, 3),   # thumb
        finger_extended(lm, 8, 6),   # index
        finger_extended(lm, 12,10),  # middle
        finger_extended(lm, 16,14),  # ring
        finger_extended(lm, 20,18)   # pinky
    ]
    up_count = sum(up)
    # print("Finger up states:", up)

    if up_count == 0:
        return "FIST"
    if up_count == 1 and up[1]:
        return "POINT"
    if up[0] and up[1] and not up[2]:
        return "THUMB_INDEX"
    return None

def send_key(action):
    keymap = {
        "PLAY": "k",       # 播放/暫停
        "PAUSE": "k",
        "FORWARD": "l",    # 快轉 10 秒
        "BACK": "j",       # 倒退 10 秒
        "SPEEDUP": ">",    # 加速
        "NORMAL": "<"      # 降速
    }
    key = keymap.get(action)
    if key:
        print(f" {action} → 按下 {key}")
        pyautogui.press(key)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            pose = classify_static_pose(lm)
            # print("Detected pose:", pose)

            if(unlock and last_time - set_time > available_time):
                unlock = False
            if(unlock):
                handle_index_direction(lm, pose)
                handle_index_play_pause(lm)
                handle_fist_speed(lm)
                handle_zoom(lm, pose)
            elif(is_meidas_touch(lm)):
                unlock = True
                set_time = time.time()


    cv2.imshow('Gesture Control', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
