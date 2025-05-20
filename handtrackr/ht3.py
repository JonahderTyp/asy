import math
import time

import cv2
import mediapipe as mp
import numpy as np

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

# Open default webcam
cap = cv2.VideoCapture(5)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Scale factor for touch threshold relative to hand size
TOUCH_SCALE = 0.5  # 30% of palm width

# Define multiple polygons as lists of (x, y) points
POLYGONS = [
    [(100, 100), (200, 80), (250, 150), (150, 200)],  # polygon 0
    [(300, 300), (400, 280), (450, 350), (350, 400)],  # polygon 1
    # Add more polygons here
]
POLY_COLOR = (255, 0, 0)  # Blue polygons
POLY_THICKNESS = 2

# Timing arrays to track touch duration and click state
touch_start_times = [None] * len(POLYGONS)
clicked_polys = [False] * len(POLYGONS)
CLICK_DURATION = 0.2  # seconds required to hold touch

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a mirror view
    # frame = cv2.flip(frame, 1)
    # rotate the frame
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    h, w, _ = frame.shape

    # Draw all polygons
    for poly in POLYGONS:
        pts = np.array(poly, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, POLY_COLOR, POLY_THICKNESS)

    # Convert BGR to RGB for processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and find hands
    result = hands.process(rgb_frame)

    touching = False
    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0),
                                    thickness=2, circle_radius=4),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # Helper to convert landmark to pixel coords
            def lm_to_px(lm):
                return int(lm.x * w), int(lm.y * h)

            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            index_mcp = hand_landmarks.landmark[5]
            pinky_mcp = hand_landmarks.landmark[17]

            x1, y1 = lm_to_px(thumb_tip)
            x2, y2 = lm_to_px(index_tip)
            x5, y5 = lm_to_px(index_mcp)
            x17, y17 = lm_to_px(pinky_mcp)

            # Compute palm width and threshold
            palm_width = math.hypot(x17 - x5, y17 - y5)
            threshold = palm_width * TOUCH_SCALE

            # Compute tip distance
            tip_distance = math.hypot(x2 - x1, y2 - y1)
            if tip_distance < threshold:
                touching = True
                # Midpoint of touch
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                # Draw contact
                cv2.circle(frame, (cx, cy), int(
                    threshold/2), (0, 0, 255), cv2.FILLED)

                # Check each polygon for timed click
                for idx, poly in enumerate(POLYGONS):
                    pts = np.array(poly, np.int32)
                    # If point inside polygon
                    if cv2.pointPolygonTest(pts, (cx, cy), False) >= 0:
                        # Start timer if not already started
                        if touch_start_times[idx] is None:
                            touch_start_times[idx] = current_time
                            clicked_polys[idx] = False
                        # If held long enough and not yet clicked
                        elif not clicked_polys[idx] and (current_time - touch_start_times[idx]) >= CLICK_DURATION:
                            print(f'Polygon {idx} clicked!')
                            clicked_polys[idx] = True
                    else:
                        # Reset if finger moves out
                        touch_start_times[idx] = None
                        clicked_polys[idx] = False

    # Overlay status
    if touching:
        cv2.putText(frame, 'Thumb & Index Touching', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # print the frame shape
    # print(frame.shape)

    # Display the frame
    # cv2.imshow('Hand Tracking', cv2.resize(frame, ()))
    cv2.imshow('Hand Tracking', frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
cv2.destroyAllWindows()
