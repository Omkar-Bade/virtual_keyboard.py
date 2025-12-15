import cv2
import mediapipe as mp
import time

# ---------------- Camera ----------------
cap = cv2.VideoCapture(0)

# ---------------- MediaPipe ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- Smoothing ----------------
prev_x, prev_y = 0, 0
alpha = 0.2

# ---------------- Typing ----------------
typed_text = ""
hover_start_time = 0
dwell_time = 0.6        # seconds (adjust if needed)
last_hovered_key = None

# ---------------- Keyboard Layout ----------------
keyboard = [
    {"keys": list("QWERTYUIOP"), "offset": 0},
    {"keys": list("ASDFGHJKL"),  "offset": 0.5},
    {"keys": list("ZXCVBNM"),    "offset": 1.0},
]

key_w = 60
key_h = 60
gap = 10

def draw_keyboard(frame, cx, cy):
    h, w, _ = frame.shape
    hovered = None

    total_rows = len(keyboard) + 1
    keyboard_height = total_rows * (key_h + gap) - gap
    max_row_width = 10 * (key_w + gap) - gap

    start_x = (w - max_row_width) // 2
    start_y = (h - keyboard_height) // 2 + 80

    y = start_y

    for row in keyboard:
        x = start_x + int(row["offset"] * (key_w + gap))
        for key in row["keys"]:
            if x < cx < x + key_w and y < cy < y + key_h:
                color = (0, 255, 0)
                hovered = key
            else:
                color = (210, 210, 210)

            cv2.rectangle(frame, (x, y), (x + key_w, y + key_h), color, -1)
            cv2.rectangle(frame, (x, y), (x + key_w, y + key_h), (0, 0, 0), 2)
            cv2.putText(frame, key, (x + 15, y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            x += key_w + gap
        y += key_h + gap

    # ---------- SPACE & BACK ----------
    space_w = key_w * 5
    back_w = key_w * 3
    sx = (w - (space_w + back_w + gap)) // 2

    if sx < cx < sx + space_w and y < cy < y + key_h:
        hovered = "SPACE"
        sc = (0, 255, 0)
    else:
        sc = (210, 210, 210)

    cv2.rectangle(frame, (sx, y), (sx + space_w, y + key_h), sc, -1)
    cv2.rectangle(frame, (sx, y), (sx + space_w, y + key_h), (0, 0, 0), 2)
    cv2.putText(frame, "SPACE", (sx + 90, y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    bx = sx + space_w + gap

    if bx < cx < bx + back_w and y < cy < y + key_h:
        hovered = "BACK"
        bc = (0, 255, 0)
    else:
        bc = (210, 210, 210)

    cv2.rectangle(frame, (bx, y), (bx + back_w, y + key_h), bc, -1)
    cv2.rectangle(frame, (bx, y), (bx + back_w, y + key_h), (0, 0, 0), 2)
    cv2.putText(frame, "BACK", (bx + 30, y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    return hovered

# ---------------- Fullscreen Window ----------------
cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    "Virtual Keyboard",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

# ---------------- Main Loop ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1280, 720))
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    cx, cy = 0, 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            tip = hand_landmarks.landmark[8]
            raw_x = int(tip.x * w)
            raw_y = int(tip.y * h)

            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = raw_x, raw_y

            cx = int(prev_x + alpha * (raw_x - prev_x))
            cy = int(prev_y + alpha * (raw_y - prev_y))
            prev_x, prev_y = cx, cy

            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)

    hovered = draw_keyboard(frame, cx, cy)

    # ---------- DWELL CLICK LOGIC ----------
    current_time = time.time()

    if hovered is not None:
        if hovered == last_hovered_key:
            if current_time - hover_start_time > dwell_time:
                if hovered == "SPACE":
                    typed_text += " "
                elif hovered == "BACK":
                    typed_text = typed_text[:-1]
                else:
                    typed_text += hovered

                hover_start_time = current_time  # prevent repeat
        else:
            last_hovered_key = hovered
            hover_start_time = current_time
    else:
        last_hovered_key = None

    # ---------- Show Typed Text ----------
    cv2.rectangle(frame, (20, 20), (1260, 80), (255, 255, 255), -1)
    cv2.putText(frame, typed_text[-40:], (30, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 0), 2)

    cv2.imshow("Virtual Keyboard", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
