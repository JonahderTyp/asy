from typing import List, Sequence

import cv2
import numpy as np

from ..datastructures import Point2Da
from .asuco import find_codes


class FrameProcessor:
    def __init__(self, frame: np.ndarray | None = None):
        self.frame = frame
        self.codes = find_codes(self.frame)
        self.center = None

        ordered_codes = [
            self.codes.get(10),
            self.codes.get(11),
            self.codes.get(12),
            self.codes.get(13),
        ]

        if all(code is not None for code in ordered_codes):
            self.center = self._intersection_from_4points(
                ordered_codes[0].center,
                ordered_codes[1].center,
                ordered_codes[2].center,
                ordered_codes[3].center
            )

    @staticmethod
    def _intersection_from_4points(TL: Point2Da, TR: Point2Da, BL: Point2Da, BR: Point2Da) -> Point2Da:
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
        return Point2Da(*intersection)

    def get_marked_frame(self) -> np.ndarray:
        marked_frame = self.frame.copy()

        for code in self.codes.values():
            # Draw the center of the code
            cv2.circle(marked_frame, tuple(code.center), 5, (0, 255, 0), -1)

        if self.center is not None:
            # Draw the center of the intersection
            cv2.circle(marked_frame, (int(self.center.x),
                       int(self.center.y)), 5, (0, 0, 255), -1)

        return marked_frame
