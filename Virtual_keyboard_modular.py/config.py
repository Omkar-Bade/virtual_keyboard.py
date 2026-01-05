# config.py

# Camera
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Hand tracking
MAX_HANDS = 1
DETECTION_CONF = 0.6
TRACKING_CONF = 0.6

# Smoothing
ALPHA = 0.2

# Keyboard timing
DWELL_TIME = 0.6
DELETE_INTERVAL = 0.35

# Keyboard UI
KEY_HEIGHT = 60
KEY_UNIT = 55
KEY_GAP = 8

# Layout
KEYBOARD_LAYOUT = [
    [("TAB",1.5),("Q",1),("W",1),("E",1),("R",1),("T",1),
     ("Y",1),("U",1),("I",1),("O",1),("P",1)],
    [("CAPS",1.8),("A",1),("S",1),("D",1),("F",1),("G",1),
     ("H",1),("J",1),("K",1),("L",1)],
    [("SHIFT",2.2),("Z",1),("X",1),("C",1),("V",1),
     ("B",1),("N",1),("M",1),("BACK",1.8)],
]
