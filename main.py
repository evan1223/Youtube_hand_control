import cv2
import mediapipe as mp
import time
from gesture_logic import GestureController

def main():
    # 初始化 MediaPipe
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=1,  # 建議先單手，避免邏輯打架，若需雙手可改為 2
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # 初始化控制器
    controller = GestureController()
    
    cap = cv2.VideoCapture(0)
    
    print("=== YouTube 手勢控制系統啟動 ===")
    print("1. ☝️ + 點擊 : 播放/暫停")
    print("2. ☝️ 左右指 : 快轉/倒退")
    print("3. 🔫 距離變大/小 : 全螢幕切換")
    print("4. ✊ 握拳 2秒 : 倍速切換")
    print("5. ✋ 左右揮 : 上/下一部影片 (分左右手)")
    print("6. ✋ 上下移 : 音量控制")
    print("7. ✋ 靜止 2秒 : 靜音切換")
    print("================================")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # 影像前處理
        frame = cv2.flip(frame, 1) # 鏡像
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb_frame)
        
        # 顯示冷卻狀態
        elapsed = time.time() - controller.last_action_time
        if elapsed < controller.cooldown:
            cv2.putText(frame, f"COOLDOWN ({1.0 - elapsed:.1f}s)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "READY", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # 繪製骨架
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 取得左右手標籤
                handedness = results.multi_handedness[idx].classification[0].label
                
                # 處理手勢邏輯
                status = controller.process(hand_landmarks.landmark, handedness)
                
                # 在手上顯示目前狀態 (除錯用)
                wrist = hand_landmarks.landmark[0]
                cx, cy = int(wrist.x * w), int(wrist.y * h)
                cv2.putText(frame, handedness, (cx, cy - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        cv2.imshow('Gesture Control', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()