# main.py

import cv2
from config import *
from hand_tracker import HandTracker
from smoother import PositionSmoother
from keyboard_ui import draw_keyboard
from input_engine import InputEngine

cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)

tracker = HandTracker(MAX_HANDS, DETECTION_CONF, TRACKING_CONF)
smoother = PositionSmoother(ALPHA)
engine = InputEngine()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame,1)
    frame = cv2.resize(frame,(FRAME_WIDTH, FRAME_HEIGHT))

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pos = tracker.get_index_tip(rgb, FRAME_WIDTH, FRAME_HEIGHT)

    cx, cy = 0, 0
    if pos:
        cx, cy = smoother.smooth(*pos)
        cv2.circle(frame,(cx,cy),10,(255,0,0),-1)

    hovered = draw_keyboard(frame, cx, cy)
    text = engine.update(hovered)

    cv2.rectangle(frame,(20,20),(1260,90),(255,255,255),-1)
    cv2.putText(frame,text[-45:],(30,70),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)

    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
