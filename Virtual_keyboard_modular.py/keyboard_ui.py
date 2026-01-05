# keyboard_ui.py

import cv2
from config import KEYBOARD_LAYOUT, KEY_UNIT, KEY_HEIGHT, KEY_GAP

def draw_keyboard(frame, cx, cy):
    h, w, _ = frame.shape
    hovered = None
    y = 220

    for row in KEYBOARD_LAYOUT:
        row_width = sum(int(KEY_UNIT*k[1]) for k in row) + KEY_GAP*(len(row)-1)
        x = (w - row_width)//2

        for key, scale in row:
            kw = int(KEY_UNIT * scale)

            if x < cx < x+kw and y < cy < y+KEY_HEIGHT:
                hovered = key
                color = (0,255,0)
            else:
                color = (210,210,210)

            cv2.rectangle(frame,(x,y),(x+kw,y+KEY_HEIGHT),color,-1)
            cv2.rectangle(frame,(x,y),(x+kw,y+KEY_HEIGHT),(0,0,0),2)
            cv2.putText(frame,key,(x+10,y+40),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2)
            x += kw + KEY_GAP
        y += KEY_HEIGHT + KEY_GAP

    # SPACE
    space_w = KEY_UNIT * 6
    sx = (w - space_w)//2

    if sx < cx < sx+space_w and y < cy < y+KEY_HEIGHT:
        hovered = "SPACE"
        color = (0,255,0)
    else:
        color = (210,210,210)

    cv2.rectangle(frame,(sx,y),(sx+space_w,y+KEY_HEIGHT),color,-1)
    cv2.rectangle(frame,(sx,y),(sx+space_w,y+KEY_HEIGHT),(0,0,0),2)
    cv2.putText(frame,"SPACE",(sx+space_w//2-45,y+40),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,0),2)

    return hovered
