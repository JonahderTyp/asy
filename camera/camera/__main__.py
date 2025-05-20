import cv2
import numpy as np


def get_full_rotation_angle(corners):
    p0 = corners[0][0]
    p1 = corners[0][1]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    angle = (np.degrees(np.arctan2(dy, dx))) % 360
    return angle


def main(camera_id=0, width=800, height=600):
    # 1. Open camera
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_id}")
        return

    # 2. Load dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    # 3. Create parameters (fallback for versions without DetectorParameters_create)
    try:
        parameters = cv2.aruco.DetectorParameters_create()
    except AttributeError:
        parameters = cv2.aruco.DetectorParameters()

    # 4. If you have OpenCV ≥4.7, you can use the new ArucoDetector API:
    if hasattr(cv2.aruco, 'ArucoDetector'):
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    else:
        detector = None

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting …")
            break

        # -- detect markers --
        if detector is not None:
            corners, ids, rejected = detector.detectMarkers(frame)
        else:
            corners, ids, rejected = cv2.aruco.detectMarkers(
                frame, aruco_dict, parameters=parameters
            )

        # -- if found, draw and compute angles --
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for corner, marker_id in zip(corners, ids.flatten()):
                angle = get_full_rotation_angle(corner)
                center = tuple(corner[0].mean(axis=0).astype(int))
                print(f"ID={marker_id}  Angle={angle:.1f}°")
                cv2.putText(frame,
                            f"ID:{marker_id} {angle:.0f}°",
                            center,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2, cv2.LINE_AA)

        # -- show and exit on 'q' --
        cv2.imshow("ArUco Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
