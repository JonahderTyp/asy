import cv2
import cv2.aruco as aruco
import numpy as np

centers = [None for _ in range(4)]


def intersection_from_4points(pts):
    """
    Given pts as a (4,2) array of 2D points [P1, P2, P3, P4],
    returns the intersection of the line P1–P4 with the line P2–P3
    as a (2,) NumPy array.
    """
    # unpack
    TL, TR, BL, BR = pts

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


def detect_aruco_markers():

    image = cv2.imread("testimg.png")
    if image is None:
        raise FileNotFoundError(f"Could not load image at 'testimg.png'")

    # Set up ArUco detector
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()

    # Initialize the camera
    # cap = cv2.VideoCapture(0)

    # Set the dictionary for ArUco markers (using 4x4 markers with 50 ids)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    # Create parameters for marker detection
    parameters = aruco.DetectorParameters()

    while True:
        # Capture frame-by-frame
        # ret, frame = cap.read()
        frame = image.copy()

        # if not ret:
        #     print("Failed to capture frame")
        #     break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        corners, ids, rejected = aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters)

        # Draw detected markers and info
        if ids is not None:
            # Draw the marker boundaries
            # frame = aruco.drawDetectedMarkers(frame, corners, ids)

            # Calculate and draw the center and pose for each marker
            for i in range(len(ids)):
                # Get the center of the marker
                corner = corners[i][0]
                center = corner.mean(axis=0)

                # Draw the center point
                cv2.circle(frame, tuple(center.astype(int)),
                           5, (0, 255, 0), -1)

                # print(type(center.astype(int)))

                centers[ids[i][0]-10] = center.astype(int)

                # Display marker ID near the center
                cv2.putText(frame, f"ID: {ids[i][0]}",
                            (int(center[0]) + 10, int(center[1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Display corner coordinates (for debugging)
                for j, point in enumerate(corner):
                    # cv2.putText(frame, f"{j}:{tuple(point.astype(int))}",
                    #             tuple(point.astype(int)),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
                    pass

        print(centers)

        p = intersection_from_4points(centers)

        print(p)

        # Draw the intersection point
        cv2.circle(frame, tuple(p.astype(int)), 5, (255, 0, 0), -1)

        # Display the resulting frame
        cv2.imshow('ArUco Marker Detection', cv2.resize(frame, (1600, 1200)))

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    # cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_aruco_markers()
