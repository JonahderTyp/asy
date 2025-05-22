import argparse
import os

import cv2
import numpy as np
from dotenv import load_dotenv

from .calibrator import calibrate
from .camera import Camera
from .mqtt_handler import MqttHandler


def main():
    try:
        camera = Camera(camera_id=0)  # , width=800, height=600)
        # image = cv2.imread("testimg.png")
        while True:
            frame = camera.get_frame()
            # frame = image.copy()

            frame = camera.process_frame(frame)

            # print(type(frame), frame.shape)

            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        camera.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Camera Capture")
    parser.add_argument(
        "--camera_id", type=int, default=0, help="Camera ID (default: 0)")
    parser.add_argument(
        "--width", type=int, default=800, help="Width of the frame (default: 800)")
    parser.add_argument(
        "--height", type=int, default=600, help="Height of the frame (default: 600)")
    parser.add_argument(
        "--calibration", action="store_true", help="Calibration mode")
    args = parser.parse_args()

    mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                       int(os.getenv("MQTT_PORT")),
                       os.getenv("MQTT_TOPIC"),
                       os.getenv("MQTT_USER"),
                       os.getenv("MQTT_PASSWORD"))

    # points_file: str = "cal_table.json"
    # with open(points_file, "r") as f:
    #     points_json: dict = json.load(f)
    #     points: list[Point2Da] = [
    #         Point2Da(float(p["x"]), float(p["y"]))
    #         for p in points_json.values()
    #     ]
    #     print(f"Loaded {len(points)} calibration points.")
    #     print(type(points))
    #     print(points)

    if args.calibration:
        calibrate(mqtt)
        exit(1)

    main()
