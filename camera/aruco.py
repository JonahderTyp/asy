import cv2
import cv2.aruco as aruco
import numpy as np


def detect_aruco_markers():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    # Set the dictionary for ArUco markers (using 4x4 markers with 50 ids)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)

    # Create parameters for marker detection
    parameters = aruco.DetectorParameters()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        corners, ids, rejected = aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters)

        # Draw detected markers and info
        if ids is not None:
            # Draw the marker boundaries
            frame = aruco.drawDetectedMarkers(frame, corners, ids)

            # Calculate and draw the center and pose for each marker
            for i in range(len(ids)):
                # Get the center of the marker
                corner = corners[i][0]
                center = corner.mean(axis=0)

                # Draw the center point
                cv2.circle(frame, tuple(center.astype(int)),
                           5, (0, 255, 0), -1)

                # Display marker ID near the center
                cv2.putText(frame, f"ID: {ids[i][0]}",
                            (int(center[0]) + 10, int(center[1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Display corner coordinates (for debugging)
                for j, point in enumerate(corner):
                    cv2.putText(frame, f"{j}:{tuple(point.astype(int))}",
                                tuple(point.astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        # Display the resulting frame
        cv2.imshow('ArUco Marker Detection', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_aruco_markers()
