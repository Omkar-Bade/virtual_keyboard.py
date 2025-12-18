import cv2
import mediapipe as mp
import time
import winsound

# ---------------- Camera ----------------
cap = cv2.VideoCapture(0)

# ---------------- MediaPipe ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- Cursor smoothing ----------------
prev_x, prev_y = 0, 0
alpha = 0.2

# ---------------- Typing state ----------------
typed_text = ""
hover_start_time = 0
dwell_time = 0.6
last_hovered_key = None
key_locked = False

caps_lock = False
shift_active = False
fn_active = False

# ---------------- Backspace timing ----------------
last_backspace_time = 0
delete_interval = 0.35

# ---------------- Symbol & FN maps ----------------
shift_symbol_map = {
    "1":"!", "2":"@", "3":"#", "4":"$", "5":"%",
    "6":"^", "7":"&", "8":"*", "9":"(", "0":")"
}

fn_map = {
    "1":"<F1>", "2":"<F2>", "3":"<F3>", "4":"<F4>", "5":"<F5>",
    "6":"<F6>", "7":"<F7>", "8":"<F8>", "9":"<F9>", "0":"<F10>"
}

# ---------------- Keyboard layout ----------------
keyboard = [
    [("FN",1.4),("1",1),("2",1),("3",1),("4",1),("5",1),("6",1),("7",1),("8",1),("9",1),("0",1)],
    [("Q",1),("W",1),("E",1),("R",1),("T",1),("Y",1),("U",1),("I",1),("O",1),("P",1)],
    [("CAPS",1.8),("A",1),("S",1),("D",1),("F",1),("G",1),("H",1),("J",1),("K",1),("L",1)],
    [("SHIFT",2.2),("Z",1),("X",1),("C",1),("V",1),("B",1),("N",1),("M",1),("BACK",1.8)],
]

key_h = 60
key_unit = 55
gap = 8

# ---------------- Draw Keyboard ----------------
def draw_keyboard(frame, cx, cy):
    h, w, _ = frame.shape
    hovered = None
    y = 220

    for row in keyboard:
        row_width = sum(int(key_unit*k[1]) for k in row) + gap*(len(row)-1)
        x = (w - row_width)//2

        for key, scale in row:
            kw = int(key_unit*scale)

            if x < cx < x+kw and y < cy < y+key_h:
                hovered = key
                color = (0,255,0)
            else:
                color = (210,210,210)

            cv2.rectangle(frame,(x,y),(x+kw,y+key_h),color,-1)
            cv2.rectangle(frame,(x,y),(x+kw,y+key_h),(0,0,0),2)

            # ---- special symbol notation (top-left) ----
            if key.isdigit() and key in shift_symbol_map:
                cv2.putText(frame, shift_symbol_map[key],
                            (x+6, y+18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                            (0,0,0), 1)

            # ---- main key label (center) ----
            ts = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            tx = x + (kw - ts[0])//2
            ty = y + (key_h + ts[1])//2

            cv2.putText(frame, key, (tx,ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0,0,0), 2)

            x += kw + gap
        y += key_h + gap

    # ---- SPACE BAR ----
    space_w = int(key_unit*6)
    sx = (w - space_w)//2

    if sx < cx < sx+space_w and y < cy < y+key_h:
        hovered = "SPACE"
        color = (0,255,0)
    else:
        color = (210,210,210)

    cv2.rectangle(frame,(sx,y),(sx+space_w,y+key_h),color,-1)
    cv2.rectangle(frame,(sx,y),(sx+space_w,y+key_h),(0,0,0),2)
    cv2.putText(frame,"SPACE",(sx+space_w//2-45,y+40),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,0),2)

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

    frame = cv2.flip(frame,1)
    frame = cv2.resize(frame,(1280,720))

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    cx, cy = 0, 0
    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        tip = hand.landmark[8]
        raw_x, raw_y = int(tip.x*1280), int(tip.y*720)
        cx = int(prev_x + alpha*(raw_x-prev_x))
        cy = int(prev_y + alpha*(raw_y-prev_y))
        prev_x, prev_y = cx, cy
        cv2.circle(frame,(cx,cy),10,(255,0,0),-1)

    hovered = draw_keyboard(frame, cx, cy)
    now = time.time()

    if hovered:
        if hovered == last_hovered_key:
            hold = now - hover_start_time

            # ---- BACKSPACE ----
            if hovered == "BACK" and hold > dwell_time:
                if now - last_backspace_time > delete_interval:
                    if hold >= 45:
                        typed_text = ""
                    elif hold >= 30:
                        typed_text = typed_text.rstrip()
                        if " " in typed_text:
                            typed_text = typed_text[:typed_text.rfind(" ")+1]
                        else:
                            typed_text = ""
                    else:
                        typed_text = typed_text[:-1]
                    last_backspace_time = now

            # ---- NORMAL INPUT ----
            elif hold > dwell_time and not key_locked:
                if hovered == "SPACE":
                    typed_text += " "

                elif hovered == "CAPS":
                    caps_lock = not caps_lock

                elif hovered == "SHIFT":
                    shift_active = True

                elif hovered == "FN":
                    fn_active = True

                else:
                    if fn_active and hovered in fn_map:
                        typed_text += fn_map[hovered]
                        fn_active = False

                    else:
                        if hovered.isdigit() and shift_active:
                            typed_text += shift_symbol_map[hovered]
                        else:
                            if caps_lock ^ shift_active:
                                typed_text += hovered.upper()
                            else:
                                typed_text += hovered.lower()
                        shift_active = False

                key_locked = True

        else:
            last_hovered_key = hovered
            hover_start_time = now
            key_locked = False
    else:
        last_hovered_key = None
        key_locked = False
        last_backspace_time = 0

    # ---- Display ----
    cv2.rectangle(frame,(20,20),(1260,90),(255,255,255),-1)
    cv2.putText(frame,typed_text[-45:],(30,70),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)

    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
