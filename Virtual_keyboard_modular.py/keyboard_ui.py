# keyboard_ui.py

import cv2
from config import (
    KEYBOARD_LAYOUT,
    NUMPAD_LAYOUT,
    SPECIAL_LAYOUT,
    ARROW_LAYOUT,
    KEY_UNIT,
    KEY_HEIGHT,
    KEY_GAP,
    FRAME_WIDTH
)

# --------------------------------------------------
# Helper: calculate row width
# --------------------------------------------------
def row_width(row):
    return sum(int(KEY_UNIT * w) for _, w in row) + KEY_GAP * (len(row) - 1)


# --------------------------------------------------
# Draw keyboard and return hovered key
# --------------------------------------------------
def draw_keyboard(frame, cx, cy, special_mode=False):
    hovered_key = None

    # -------- SELECT MAIN LAYOUT --------
    main_layout = SPECIAL_LAYOUT if special_mode else KEYBOARD_LAYOUT

    # -------- CALCULATE CENTER X --------
    max_row_w = max(row_width(row) for row in main_layout)
    start_x = (FRAME_WIDTH - max_row_w) // 2
    start_y = 140

    # -------- DRAW MAIN KEYBOARD --------
    y = start_y
    for row in main_layout:
        x = start_x
        for key, w_mul in row:
            w = int(KEY_UNIT * w_mul)
            x1, y1 = x, y
            x2, y2 = x + w, y + KEY_HEIGHT

            # Draw key
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)
            cv2.putText(frame, key, (x1 + 10, y1 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            # Hover detection
            if cx is not None and x1 < cx < x2 and y1 < cy < y2:
                hovered_key = key
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 3)

            x += w + KEY_GAP
        y += KEY_HEIGHT + KEY_GAP

    # -------- NUMPAD (RIGHT SIDE) --------
    np_x = start_x + max_row_w + 60
    np_y = start_y

    y = np_y
    for row in NUMPAD_LAYOUT:
        x = np_x
        for key, w_mul in row:
            w = int(KEY_UNIT * w_mul)
            x1, y1 = x, y
            x2, y2 = x + w, y + KEY_HEIGHT

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)
            cv2.putText(frame, key, (x1 + 10, y1 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            if cx is not None and x1 < cx < x2 and y1 < cy < y2:
                hovered_key = key
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 3)

            x += w + KEY_GAP
        y += KEY_HEIGHT + KEY_GAP

    # -------- ARROW KEYS (BOTTOM CENTER) --------
    arrow_w = max(row_width(row) for row in ARROW_LAYOUT)
    arrow_x = (FRAME_WIDTH - arrow_w) // 2
    arrow_y = y + 40

    y = arrow_y
    for row in ARROW_LAYOUT:
        x = arrow_x
        for key, w_mul in row:
            w = int(KEY_UNIT * w_mul)
            x1, y1 = x, y
            x2, y2 = x + w, y + KEY_HEIGHT

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,255,255), 2)
            cv2.putText(frame, key, (x1 + 18, y1 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

            if cx is not None and x1 < cx < x2 and y1 < cy < y2:
                hovered_key = key
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 3)

            x += w + KEY_GAP
        y += KEY_HEIGHT + KEY_GAP

    return hovered_key
