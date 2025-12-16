import cv2
import mediapipe as mp
import time

# 匯入所有功能模組
from index_direction import handle_index_direction
from index_play_pause import handle_index_play_pause
from zoom_inout import handle_zoom
from fist_speed_control import handle_fist_speed
from swipe_control import handle_swipe
from volume_control import handle_volume
from mute_control import handle_mute

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# --- 狀態管理 ---
is_unlocked = False       # 預設鎖定
unlock_timeout = 3.0      # 解鎖後幾秒沒動作自動鎖回
last_unlock_time = 0      
cooldown_state = {'swipe': 0} # 揮動冷卻

def finger_extended(lm, tip, pip, thresh=0.1):
    return abs(lm[tip].x - lm[pip].x) > thresh or abs(lm[tip].y - lm[pip].y) > thresh

def classify_static_pose(lm):
    up = [
        finger_extended(lm, 4, 3), 
        # lm[3].y - lm[4].y > 1,  
        finger_extended(lm, 8, 6),   
        finger_extended(lm, 12,10),  
        finger_extended(lm, 16,14),  
        finger_extended(lm, 20,18)   
    ]
    up_count = sum(up)

    # 用來判斷小拇指解鎖 (只有小拇指伸直)
    # if up_count == 2 and up[4]: 
    #     return "PINKY"
    if up[1] and up[2] and not up[3]: 
        return "PINKY"
    
    # 為了避免判斷干擾，保留原本的判斷，但在這個架構下主要依賴個別模組
    if up_count == 0: return "FIST"
    if up_count == 1 and up[1]: return "POINT"
    
    return "OTHER"

print("程式啟動：狀態 [LOCKED]")
print("請對鏡頭比出「小拇指」解鎖，解鎖後執行一個動作即會自動鎖定。")

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()

    # --- 1. 逾時自動鎖定 ---
    if is_unlocked and (current_time - last_unlock_time > unlock_timeout):
        is_unlocked = False
        print("⏳ 逾時：系統已鎖定 (LOCKED)")

    # --- 2. 顯示狀態 ---
    if is_unlocked:
        status_text = "STATUS: UNLOCKED (Ready)"
        color = (0, 255, 0) # Green
    else:
        status_text = "STATUS: LOCKED (Show Pinky)"
        color = (0, 0, 255) # Red
    
    cv2.putText(frame, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # 取得手勢與左右手
            pose = classify_static_pose(lm)
            hand_label = results.multi_handedness[idx].classification[0].label if results.multi_handedness else "Unknown"

            # --- 3. 判斷解鎖 (PINKY) ---
            if pose == "PINKY":
                is_unlocked = True
                last_unlock_time = current_time
                # cv2.putText(frame, "PINKY DETECTED", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # --- 4. 執行功能 (只有在 UNLOCKED 時執行) ---
            if is_unlocked:
                action_taken = False
                
                # 依序執行並檢查是否觸發動作 (使用 or 並不是好方法，因為要確保 function 被執行)
                # 我們用變數累加的方式
                
                if handle_swipe(lm, hand_label, cooldown_state): action_taken = True
                if handle_volume(lm): action_taken = True
                if handle_mute(lm): action_taken = True
                if handle_index_direction(lm, pose): action_taken = True
                if handle_index_play_pause(lm): action_taken = True
                if handle_zoom(lm, pose): action_taken = True
                if handle_fist_speed(lm): action_taken = True # 倍速結束時才會回傳 True
                
                # --- 5. 執行完畢後鎖定 ---
                if action_taken:
                    print("🔒 動作執行完畢：系統鎖定 (LOCKED)")
                    is_unlocked = False

    cv2.imshow('Gesture Control', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()