import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self):
        # Initialize MediaPipe Hands.
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        # Configure the Hands model:
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def process_frame(self, frame: cv2.Mat) -> cv2.Mat:
        # Flip the frame horizontally for a mirror view
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2RGB)

        # Process the frame and find hands
        result = self.hands.process(rgb_frame)

        # Draw hand landmarks
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(
                        color=(0, 255, 0), thickness=2, circle_radius=4),
                    self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

        return frame
