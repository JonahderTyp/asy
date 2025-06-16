import cv2
import cv2.aruco as aruco

from ..datastructures import Point2Da


class Code:
    def __init__(self, id: int, center: Point2Da | None = None):
        self.id = id
        self.center = center

    def __str__(self):
        return f"Code: {self.id}"

    def __repr__(self):
        return f"Code({self.id})"


def find_codes(
        frame,
        aruco_dict=aruco.getPredefinedDictionary(aruco.DICT_4X4_50),
        parameters=aruco.DetectorParameters()) -> dict[str, Code]:
    """
    Find ArUco codes in the given frame.
    """

    codes = {}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect markers
    corners, ids, rejected = cv2.aruco.ArucoDetector(
        aruco_dict, parameters).detectMarkers(frame)
    # corners, ids, rejected = aruco.detectMarkers(
    #     gray, aruco_dict, parameters=parameters)

    if ids is not None:
        for i in range(len(ids)):
            # Get the center of the marker
            corner = corners[i][0]
            center = corner.mean(axis=0)
            center = Point2Da(center[0], center[1])
            code = Code(ids[i][0], center)
            codes[code.id] = code

    return codes
