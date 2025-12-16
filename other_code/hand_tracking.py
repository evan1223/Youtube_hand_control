# hand_tracking.py
import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, max_hands=2, detection_con=0.7, track_con=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """偵測手部並回傳處理結果"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img, self.results

    def get_hand_info(self, img, hand_index=0):
        """獲取特定手部的座標與標籤(左/右)"""
        lm_list = []
        hand_label = None
        
        if self.results.multi_hand_landmarks:
            if hand_index < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_index]
                
                # 獲取左右手標籤
                classification = self.results.multi_handedness[hand_index]
                hand_label = classification.classification[0].label
                
                # 獲取座標
                h, w, c = img.shape
                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                    
        return lm_list, hand_label