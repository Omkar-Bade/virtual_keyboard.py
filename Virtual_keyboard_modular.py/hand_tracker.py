# hand_tracker.py

import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands, det_conf, track_conf):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf
        )

    def get_index_tip(self, rgb_frame, w, h):
        result = self.hands.process(rgb_frame)
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            tip = hand.landmark[8]
            return int(tip.x * w), int(tip.y * h)
        return None
