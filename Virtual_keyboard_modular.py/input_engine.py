# input_engine.py

import time
import winsound
from config import DWELL_TIME, DELETE_INTERVAL

class InputEngine:
    def __init__(self):
        self.typed_text = ""
        self.last_key = None
        self.hover_start = 0
        self.key_locked = False

        self.caps = False
        self.shift = False

        self.last_backspace_time = 0

    def update(self, hovered):
        now = time.time()

        # -------------------------------
        # NO KEY HOVERED
        # -------------------------------
        if hovered is None:
            self.last_key = None
            self.key_locked = False
            return self.typed_text

        # -------------------------------
        # NEW KEY HOVER START
        # -------------------------------
        if hovered != self.last_key:
            self.last_key = hovered
            self.hover_start = now
            self.key_locked = False
            return self.typed_text

        # -------------------------------
        # SAME KEY HOVERING
        # -------------------------------
        hold_time = now - self.hover_start

        # -------------------------------
        # BACKSPACE (repeatable)
        # -------------------------------
        if hovered == "BACK" and hold_time > DWELL_TIME:
            if now - self.last_backspace_time > DELETE_INTERVAL:
                winsound.Beep(600, 30)
                self.typed_text = self.typed_text[:-1]
                self.last_backspace_time = now
            return self.typed_text

        # -------------------------------
        # PREVENT MULTIPLE TYPING
        # -------------------------------
        if self.key_locked or hold_time < DWELL_TIME:
            return self.typed_text

        # -------------------------------
        # KEY ACTIVATION (ONCE)
        # -------------------------------
        winsound.Beep(800, 50)

        if hovered == "SPACE":
            self.typed_text += " "

        elif hovered == "TAB":
            self.typed_text += "    "  # 4 spaces

        elif hovered == "CAPS":
            self.caps = not self.caps

        elif hovered == "SHIFT":
            self.shift = True

        else:
            char = hovered.upper() if self.caps ^ self.shift else hovered.lower()
            self.typed_text += char
            self.shift = False

        # -------------------------------
        # LOCK KEY UNTIL FINGER LEAVES
        # -------------------------------
        self.key_locked = True

        return self.typed_text
