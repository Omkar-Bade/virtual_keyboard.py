import cv2
import mediapipe as mp

# Webcam
cap = cv2.VideoCapture(0)

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

while True:
    success, frame = cap.read()
    if not success:
        break

    # Mirror image
    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand detection
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw hand skeleton
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Index fingertip = landmark 8
            index_finger_tip = hand_landmarks.landmark[8]

            # Convert normalized coordinates to pixel values
            x = int(index_finger_tip.x * w)
            y = int(index_finger_tip.y * h)

            # Draw fingertip point
            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

            # Show coordinates
            cv2.putText(
                frame,
                f"Index Finger: ({x}, {y})",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Step 2 - Fingertip Tracking", frame)

    # ESC key to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()