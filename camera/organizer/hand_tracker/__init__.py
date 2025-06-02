import cv2
import mediapipe as mp

from ..datastructures import Point2Da


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands_model = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        self.last_hand_landmarks = None
        self.last_frame_shape = (0, 0)  # (height, width)

    def detect_hands(self, frame: cv2.Mat) -> cv2.Mat:
        frame = frame.copy()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands_model.process(rgb_frame)

        self.last_hand_landmarks = result.multi_hand_landmarks
        # Save frame shape for pixel conversion
        self.last_frame_shape = frame.shape[:2]

        if self.last_hand_landmarks:
            for hand_landmarks in self.last_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(
                        color=(0, 255, 0), thickness=2, circle_radius=4),
                    self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

        return frame

    def get_hand_positions(self) -> list[list[Point2Da]]:
        if not self.last_hand_landmarks:
            return []

        height, width = self.last_frame_shape
        hand_positions = []

        for hand_landmarks in self.last_hand_landmarks:
            landmarks = [
                Point2Da(
                    x=int(landmark.x * width),
                    y=int(landmark.y * height)
                )
                for landmark in hand_landmarks.landmark
            ]
            hand_positions.append(landmarks)

        return hand_positions
