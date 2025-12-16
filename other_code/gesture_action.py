# gesture_action.py
import time
import math
import cv2
import pyautogui
import config

class GestureController:
    def __init__(self):
        self.prev_positions = {}      
        self.last_action_time = 0
        self.mute_start_time = 0
        self.is_mute_counting = False
        
        # 為了避免音量調太快，我們加一個簡單的計數器來控制速度
        self.vol_frame_count = 0 

    def is_palm_open(self, lm_list):
        """判斷手掌是否張開 (用於靜音)"""
        if not lm_list: return False
        fingers_open = 0
        if lm_list[8][2] < lm_list[6][2]: fingers_open += 1
        if lm_list[12][2] < lm_list[10][2]: fingers_open += 1
        if lm_list[16][2] < lm_list[14][2]: fingers_open += 1
        if lm_list[20][2] < lm_list[18][2]: fingers_open += 1
        return fingers_open >= 3

    def process_gesture(self, hand_index, hand_label, lm_list, img):
        if not lm_list: return

        current_time = time.time()
        cx, cy = lm_list[0][1], lm_list[0][2] # 手腕座標

        # 計算手腕滑動位移 (用於切換影片)
        dx = 0
        if hand_index in self.prev_positions:
            dx = cx - self.prev_positions[hand_index]['x']

        status_text = None

        # ---------------------------------------------------------
        # 功能 A: 音量控制 (狀態觸發：張開持續大聲，捏合持續小聲)
        # ---------------------------------------------------------
        # 取得拇指(4) 與 食指(8) 的座標
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        
        # 畫圖
        cx_mid, cy_mid = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        # 計算目前的距離
        curr_dist = math.hypot(x2 - x1, y2 - y1)
        
        # 顯示目前距離數值 (方便您除錯調整參數)
        cv2.putText(img, f"Dist: {int(curr_dist)}", (x1+20, y1-20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # --- 核心邏輯修改 ---
        # 只要距離大於設定值 -> 持續大聲
        if curr_dist > config.DIST_MAX_TRIGGER:
            print("Action: 持續變大聲 (Open)")
            pyautogui.press(config.KEY_VOL_UP)
            
            # 視覺回饋：大綠點
            cv2.circle(img, (cx_mid, cy_mid), 15, (0, 255, 0), cv2.FILLED)
            cv2.putText(img, "VOL UP", (cx_mid-30, cy_mid-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 只要距離小於設定值 -> 持續小聲
        elif curr_dist < config.DIST_MIN_TRIGGER:
            print("Action: 持續變小聲 (Close)")
            pyautogui.press(config.KEY_VOL_DOWN)
            
            # 視覺回饋：大紅點
            cv2.circle(img, (cx_mid, cy_mid), 15, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, "VOL DOWN", (cx_mid-40, cy_mid-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        else:
            # 中間休息區 (灰色點)
            cv2.circle(img, (cx_mid, cy_mid), 8, (150, 150, 150), cv2.FILLED)

        # ---------------------------------------------------------
        # 功能 B: 切換影片 (手腕水平滑動)
        # ---------------------------------------------------------
        if current_time - self.last_action_time > config.COOLDOWN_TIME:
            if abs(dx) > config.SWIPE_THRESHOLD:
                if dx < 0 and hand_label == "Left": 
                    print("Action: 上一部")
                    pyautogui.hotkey(*config.KEY_PREV)
                    self.last_action_time = current_time
                    return "Previous Video"
                elif dx > 0 and hand_label == "Right": # 建議用左手，避免右手音量誤觸
                    print("Action: 下一部")
                    pyautogui.hotkey(*config.KEY_NEXT)
                    self.last_action_time = current_time
                    return "Next Video"

        # ---------------------------------------------------------
        # 功能 C: 靜音判斷
        # ---------------------------------------------------------
        is_open = self.is_palm_open(lm_list)
        
        dy = 0
        if hand_index in self.prev_positions:
            dy = cy - self.prev_positions[hand_index]['y']
            
        is_still = False
        if abs(dx) < config.STILL_THRESHOLD and abs(dy) < config.STILL_THRESHOLD:
            is_still = True

        if is_open and is_still:
            if not self.is_mute_counting:
                self.mute_start_time = current_time
                self.is_mute_counting = True
            
            remaining = config.MUTE_HOLD_TIME - (current_time - self.mute_start_time)
            if remaining > 0:
                cv2.putText(img, f"Mute: {remaining:.1f}s", (cx, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            elif current_time - self.last_action_time > config.COOLDOWN_TIME:
                print("Action: 靜音切換")
                pyautogui.press(config.KEY_MUTE)
                self.last_action_time = current_time
                self.is_mute_counting = False
                return "Mute Toggled"
        else:
            self.is_mute_counting = False

        # 更新歷史紀錄
        self.prev_positions[hand_index] = {'x': cx, 'y': cy}
        
        return status_text