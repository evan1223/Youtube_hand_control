import time
import pyautogui
import hand_math

class GestureController:
    def __init__(self):
        self.last_action_time = 0
        self.cooldown = 1.0
        
        # 狀態變數
        self.prev_wrist_x = None
        self.prev_wrist_y = None
        self.prev_index_y = None
        self.prev_pinch_dist = None
        
        self.fist_start_time = None
        self.mute_start_time = None
        
        self.pointing_mode = False 
        self.speed_doubled = False

    def execute_action(self, action_name, key_code=None, is_hotkey=False):
        current_time = time.time()
        print(f"🔥 觸發動作：{action_name}")
        
        if key_code:
            if is_hotkey:
                pyautogui.hotkey(*key_code)
            else:
                pyautogui.press(key_code)
                
        self.last_action_time = current_time
        # 重置所有變數，避免連續誤觸
        self.prev_wrist_x = None
        self.prev_wrist_y = None
        self.prev_pinch_dist = None
        self.mute_start_time = None
        self.pointing_mode = False

    def process(self, lm, handedness_label):
        current_time = time.time()
        
        # 全域冷卻
        if current_time - self.last_action_time < self.cooldown:
            return "COOLDOWN"

        tips = [4, 8, 12, 16, 20]
        pips = [3, 7, 11, 15, 19]
        mcps = [2, 6, 10, 14, 18]

        # 1. 判斷手指伸直狀態
        fingers_up = [hand_math.is_finger_straight(lm, tips, pips, mcps, i) for i in range(5)]
        
        wrist = lm[0]
        index_tip = lm[8]
        index_mcp = lm[5]

        # -------------------------------------------------------------------
        # 動作 A: 食指類 (點擊 / 快轉)
        # -------------------------------------------------------------------
        is_index_only = fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]
        
        if is_index_only:
            # 判斷食指方向
            diff_x = abs(index_tip.x - index_mcp.x)
            diff_y = abs(index_tip.y - index_mcp.y)
            
            is_vertical = diff_y > diff_x  # 指向上下
            is_horizontal = diff_x > diff_y # 指向左右
            
            # 判斷手心是否朝向鏡頭 (利用 Thumb/Pinky 相對位置)
            # 點擊時，通常手背不會朝自己，所以適用 Facing Down/Camera 的邏輯 (拇指在內側)
            # is_facing_front = hand_math.is_palm_facing_down_or_camera(lm, handedness_label)

            # --- 1. 點擊 (垂直 + 手心朝鏡頭 + 下壓) ---
            if is_vertical and lm[4].x > lm[3].x:
                self.pointing_mode = True
                if self.prev_index_y is not None:
                    dy = index_tip.y - self.prev_index_y
                    if dy > 0.03: # 下壓
                        self.execute_action("播放/暫停", "k")
                        return
                self.prev_index_y = index_tip.y
                
            # --- 2. 快轉/倒退 (水平指向) ---
            elif is_horizontal:
                self.pointing_mode = False # 切換到水平模式，重置點擊
                self.prev_index_y = None
                
                dx_finger = index_tip.x - index_mcp.x
                if handedness_label == "Right" and dx_finger > 0.05:
                    self.execute_action("快轉 5 秒", "right")
                    return
                elif handedness_label == "Left" and dx_finger < -0.05:
                    self.execute_action("倒退 5 秒", "left")
                    return
            else:
                self.pointing_mode = False
                self.prev_index_y = None
        else:
            self.pointing_mode = False
            self.prev_index_y = None

        # -------------------------------------------------------------------
        # 動作 B: 縮放 (槍手勢)
        # -------------------------------------------------------------------
        is_gun = fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]
        if is_gun and lm[4].x < lm[3].x:
            curr_dist = hand_math.get_distance(lm[4], lm[8])
            if self.prev_pinch_dist:
                delta = curr_dist - self.prev_pinch_dist
                if delta > 0.015: 
                    self.execute_action("放大螢幕", "f")
                    return
                elif delta < -0.015:
                    self.execute_action("縮小螢幕", "f")
                    return
            self.prev_pinch_dist = curr_dist
        else:
            self.prev_pinch_dist = None

        # -------------------------------------------------------------------
        # 動作 C: 倍速 (握拳)
        # -------------------------------------------------------------------
        if hand_math.is_fist(lm):
            if self.fist_start_time is None: self.fist_start_time = current_time
            elif current_time - self.fist_start_time > 2.0:
                self.speed_doubled = not self.speed_doubled
                if self.speed_doubled:
                    self.execute_action("開啟 2 倍速", ('shift', '>'), True)
                else:
                    self.execute_action("結束 2 倍速", ('shift', '<'), True)
                self.fist_start_time = None
                return
        else:
            self.fist_start_time = None

        # -------------------------------------------------------------------
        # 動作 D: 手掌類 (Open Palm) - 音量 / 靜音 / 換片
        # -------------------------------------------------------------------
        is_palm_open = all(fingers_up)
        
        if is_palm_open:
            # 1. 判斷手掌姿態
            is_up = hand_math.is_palm_facing_up(lm, handedness_label)           # 手心向上 (Thumb外側)
            is_down_cam = hand_math.is_palm_facing_down_or_camera(lm, handedness_label) # 手心向下/鏡頭 (Thumb內側)

            # 2. 計算手腕移動
            move_x = 0
            move_y = 0
            is_moving = False
            
            if self.prev_wrist_x is not None:
                move_x = wrist.x - self.prev_wrist_x
                move_y = wrist.y - self.prev_wrist_y
                # 判斷是否在移動 (閾值)
                if abs(move_x) > 0.01 or abs(move_y) > 0.01:
                    is_moving = True
            
            MOVE_THRESH = 0.025

            # --- 3. 音量變大 (手心向上 + 往上移) ---
            if is_up:
                self.mute_start_time = None # 手心向上絕不觸發靜音
                # 檢查垂直移動
                if abs(move_y) > abs(move_x) and abs(move_y) > MOVE_THRESH:
                    if move_y < 0: # Y變小 = 往上
                        self.execute_action("音量調大 (手心上)", "volumeup")
                        return

            # --- 4. 音量變小 (手心向下 + 往下移) ---
            if is_down_cam:
                # 檢查垂直移動
                if abs(move_y) > abs(move_x) and abs(move_y) > MOVE_THRESH:
                    if move_y > 0: # Y變大 = 往下
                        self.execute_action("音量調小 (手心下)", "volumedown")
                        return

            # --- 5. 靜音 (手心向下/向鏡頭 + 靜止) ---
            # 因為音量小也需要手心向下，所以必須用「is_moving」來區分
            if is_down_cam and not is_moving:
                if self.mute_start_time is None:
                    self.mute_start_time = current_time
                elif current_time - self.mute_start_time > 2.0:
                    self.execute_action("靜音切換", "m")
                    return
            else:
                self.mute_start_time = None

            # --- 6. 換片 (手心向上/向內 + 左右揮) ---
            # 通常揮動時，手會稍微側一點，狀態可能介於 Up 和 Inward 之間
            # 只要是「水平揮動」且「不是手心向下(避免音量誤觸)」，就允許觸發
            # 或者嚴格一點：必須是 Facing Up (手刀態大拇指也是在外側)
            if is_up: 
                if abs(move_x) > abs(move_y) and abs(move_x) > MOVE_THRESH:
                    if handedness_label == "Right" and move_x < 0: # 右手向左
                        self.execute_action("下一部影片", ('shift', 'n'), True)
                        return
                    if handedness_label == "Left" and move_x > 0: # 左手向右
                        self.execute_action("上一部影片", ('shift', 'p'), True)
                        return

            self.prev_wrist_x = wrist.x
            self.prev_wrist_y = wrist.y
        else:
            self.prev_wrist_x = None
            self.prev_wrist_y = None
            self.mute_start_time = None

        return "IDLE"