import cv2
import mediapipe as mp
import time
import winsound

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- Typing State ----------------
typed_text = ""
dwell_time = 0.6
caps_lock = False
shift_active = False

# ---------------- Keyboard Layout ----------------
keyboard = [
    [("TAB", 1.5), ("Q",1),("W",1),("E",1),("R",1),("T",1),("Y",1),("U",1),("I",1),("O",1),("P",1)],
    [("CAPS",1.8),("A",1),("S",1),("D",1),("F",1),("G",1),("H",1),("J",1),("K",1),("L",1)],
    [("SHIFT",2.2),("Z",1),("X",1),("C",1),("V",1),("B",1),("N",1),("M",1),("BACK",1.8)],
]

key_h = 60
key_unit = 55
gap = 8

# ---------------- Multi-finger State ----------------
fingers = {
    4: {"last": None, "start": 0, "locked": False},   # Thumb
    8: {"last": None, "start": 0, "locked": False},   # Index
    12: {"last": None, "start": 0, "locked": False},  # Middle
    16: {"last": None, "start": 0, "locked": False},  # Ring
    20: {"last": None, "start": 0, "locked": False},  # Pinky
}

# ---------------- Draw Keyboard ----------------
def draw_keyboard(frame, x, y):
    h, w, _ = frame.shape
    hovered = None

    keyboard_height = (len(keyboard) + 1) * (key_h + gap)
    start_y = (h - keyboard_height) // 2 + 70
    cy = start_y

    for row in keyboard:
        row_width = sum(int(key_unit * k[1]) for k in row) + gap*(len(row)-1)
        cx = (w - row_width) // 2

        for key, scale in row:
            kw = int(key_unit * scale)

            if cx < x < cx + kw and cy < y < cy + key_h:
                hovered = key
                color = (0, 255, 0)
            else:
                color = (210, 210, 210)

            cv2.rectangle(frame, (cx, cy), (cx + kw, cy + key_h), color, -1)
            cv2.rectangle(frame, (cx, cy), (cx + kw, cy + key_h), (0, 0, 0), 2)

            ts = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            tx = cx + (kw - ts[0]) // 2
            ty = cy + (key_h + ts[1]) // 2

            cv2.putText(frame, key, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            cx += kw + gap
        cy += key_h + gap

    # SPACE
    space_w = int(key_unit * 6)
    sx = (w - space_w) // 2

    if sx < x < sx + space_w and cy < y < cy + key_h:
        hovered = "SPACE"
        sc = (0, 255, 0)
    else:
        sc = (210, 210, 210)

    cv2.rectangle(frame, (sx, cy), (sx + space_w, cy + key_h), sc, -1)
    cv2.rectangle(frame, (sx, cy), (sx + space_w, cy + key_h), (0, 0, 0), 2)
    cv2.putText(frame, "SPACE", (sx + space_w//2 - 40, cy + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    return hovered

# ---------------- Fullscreen ----------------
cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Virtual Keyboard",
                      cv2.WND_PROP_FULLSCREEN,
                      cv2.WINDOW_FULLSCREEN)

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

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            for fid in fingers.keys():
                tip = hand_landmarks.landmark[fid]
                x = int(tip.x * w)
                y = int(tip.y * h)

                cv2.circle(frame, (x, y), 8, (255, 0, 0), -1)

                hovered = draw_keyboard(frame, x, y)
                state = fingers[fid]
                now = time.time()

                if hovered:
                    if hovered == state["last"]:
                        if not state["locked"] and (now - state["start"] > dwell_time):
                            winsound.Beep(800, 70)

                            if hovered == "SPACE":
                                typed_text += " "
                            elif hovered == "BACK":
                                typed_text = typed_text[:-1]
                            elif hovered == "TAB":
                                typed_text += "\t"
                            elif hovered == "CAPS":
                                caps_lock = not caps_lock
                            elif hovered == "SHIFT":
                                shift_active = True
                            else:
                                char = hovered.upper() if (caps_lock or shift_active) else hovered.lower()
                                typed_text += char
                                shift_active = False

                            state["locked"] = True
                    else:
                        state["last"] = hovered
                        state["start"] = now
                        state["locked"] = False
                else:
                    state["last"] = None
                    state["locked"] = False

    # Display text
    cv2.rectangle(frame, (20, 20), (1260, 90), (255, 255, 255), -1)
    cv2.putText(frame, typed_text[-45:], (30, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    cv2.imshow("Virtual Keyboard", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
