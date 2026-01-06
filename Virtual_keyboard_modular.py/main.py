# main.py

import cv2
from config import *
from hand_tracker import HandTracker
from smoother import PositionSmoother
from keyboard_ui import draw_keyboard
from input_engine import InputEngine

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# ================= FULLSCREEN WINDOW =================
WINDOW_NAME = "Virtual Keyboard"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

# ================= OBJECTS =================
tracker = HandTracker(MAX_HANDS, DETECTION_CONF, TRACKING_CONF)
smoother = PositionSmoother(ALPHA)
engine = InputEngine()

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # ---------- HAND TRACKING ----------
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pos = tracker.get_index_tip(rgb, FRAME_WIDTH, FRAME_HEIGHT)

    cx, cy = None, None
    if pos:
        cx, cy = smoother.smooth(*pos)
        cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)
    else:
        smoother.reset()

    # ---------- KEYBOARD ----------
    hovered = draw_keyboard(frame, cx, cy, engine.special_mode)

    # ---------- INPUT ENGINE ----------
    typed_text, cursor, _ = engine.update(hovered)

    # ---------- TEXT DISPLAY ----------
    cv2.rectangle(frame, (20, 20), (FRAME_WIDTH - 20, 90), (255, 255, 255), -1)

    display_text = typed_text[:cursor] + "|" + typed_text[cursor:]
    cv2.putText(
        frame,
        display_text[-70:],  # more chars for fullscreen
        (30, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 0),
        2
    )

    # ---------- SHOW ----------
    cv2.imshow(WINDOW_NAME, frame)

    # ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# ================= CLEANUP =================
cap.release()
cv2.destroyAllWindows()
