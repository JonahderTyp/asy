import cv2
import mediapipe as mp
import pyautogui

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Get screen size for mapping
screen_width, screen_height = pyautogui.size()

# Open default webcam
cap = cv2.VideoCapture(5)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror the frame for natural interaction
    # frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert BGR to RGB for processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        # Optional: draw hand landmarks
        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 0),
                                thickness=2, circle_radius=4),
            mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

        # Map the index fingertip to screen coordinates
        ix = hand_landmarks.landmark[8].x
        iy = hand_landmarks.landmark[8].y
        screen_x = screen_width * (1 - ix)  # mirrored horizontally
        screen_y = screen_height * iy

        # Move cursor directly without smoothing for better performance
        pyautogui.moveTo(screen_x, screen_y)

        # Display cursor position
        cv2.putText(frame, f'Cursor: {int(screen_x)}, {int(screen_y)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show the video feed
    cv2.imshow('Hand Tracking Control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
