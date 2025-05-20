import cv2
import mediapipe as mp

# Initialize MediaPipe Hands.
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Configure the Hands model:
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Button settings
window_name = 'Hand Tracking'
button_pos = (10, 10)   # Top-left corner of button (x, y)
button_size = (100, 40)  # Width and height (w, h)
button_text = 'Click Me'
in_button = False      # State flag for virtual click

# Open default webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Create display window
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Mirror image and prepare RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame for hand landmarks
    result = hands.process(rgb_frame)

    # Reset click flag if no hand detected
    finger_inside = False
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks,
                                   mp_hands.HAND_CONNECTIONS)
            # Get index finger tip coords
            lm = hand_landmarks.landmark[8]
            h, w, _ = frame.shape
            x_px, y_px = int(lm.x * w), int(lm.y * h)
            # Print coords
            # print(f"Pointer Finger Tip Coordinates: x={x_px}, y={y_px}")
            # Check if fingertip is over button region
            bx, by = button_pos
            bw, bh = button_size
            if bx <= x_px <= bx + bw and by <= y_px <= by + bh:
                finger_inside = True

    # Virtual click detection
    if finger_inside and not in_button:
        print("Button clicked!")
        in_button = True
    elif not finger_inside:
        in_button = False

    # Draw semi-transparent button overlay
    overlay = frame.copy()
    bx, by = button_pos
    bw, bh = button_size
    cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (50, 50, 50), -1)
    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (255, 255, 255), 1)
    cv2.putText(frame, button_text, (bx + 10, by + 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2)

    # Display frame
    cv2.imshow(window_name, frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
