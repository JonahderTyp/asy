import cv2
import cv2.aruco as aruco
import numpy as np

from ..datastructures import Point2D
from .asuco import Code, find_codes


class Camera:
    def __init__(self, camera_id=0, width: int | None = None, height: int | None = None):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = cv2.VideoCapture(camera_id)
        if width is not None and height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open camera {camera_id}")

    @staticmethod
    def _intersection_from_4points(TL: Point2D, TR: Point2D, BL: Point2D, BR: Point2D):
        """
        Given pts as a (4,2) array of 2D points [TL, TR, BL, BR],
        returns the intersection of the line P1-P4 with the line P2-P3
        as a (2,) NumPy array.
        """
        # unpack

        # direction vectors
        r = BR - TL     # from P1 toward P4
        s = BL - TR     # from P2 toward P3

        # build the matrix [r  -s] and right-hand side (P2 - P1)
        M = np.column_stack((r, -s))   # shape (2,2)
        b = TR - TL                     # shape (2,)

        # check for parallelism
        det = np.linalg.det(M)
        if np.isclose(det, 0):
            raise ValueError(
                "The two lines are parallel (or nearly so); no unique intersection.")

        # solve for [t, u]
        t, u = np.linalg.solve(M, b)

        # intersection point on line P1 + t·r
        intersection = TL + t * r
        return intersection

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Can't receive frame")
        return frame

    def process_frame(self, frame: np.ndarray | None = None):
        codes = find_codes(frame)
        # print(codes)

        for code in codes:
            # Draw the center of the code
            cv2.circle(frame, tuple(code.center), 5, (0, 255, 0), -1)

        return frame

    def release(self):
        self.cap.release()
