import argparse
import json
import os

import cv2
import numpy as np
from dotenv import load_dotenv

from .calibrator import calibrate_projector
from .camera import Camera
from .camera.calibrate import calibrate_camera
from .datastructures import Playfield, Point2Da
from .mqtt_handler import MqttHandler
from .pcb_tracker import FrameProcessor
from .transformer import HomographyTransformer


def load_transformer(source_points_file: str, target_points_file: str) -> HomographyTransformer:
    with open(source_points_file, "r") as f:
        points_json: dict = json.load(f)
        source_points: list[Point2Da] = [
            Point2Da(float(p["x"]), float(p["y"]))
            for p in points_json.values()
        ]
        print(f"Loaded {len(source_points)} source calibration points.")
        # print(type(source_points))
        # print(source_points)

    with open(target_points_file, "r") as f:
        points_json: dict = json.load(f)
        target_points: list[Point2Da] = [
            Point2Da(float(p["x"]), float(p["y"]))
            for p in points_json.values()
        ]
        print(f"Loaded {len(target_points)} target calibration points.")
        # print(type(target_points))
        # print(target_points)

    if len(source_points) != len(target_points):
        raise ValueError(
            f"Source and target points must have the same number of points. "
            f"Got {len(source_points)} and {len(target_points)}."
        )

    if len(source_points) < 4:
        raise ValueError(
            f"Need at least 4 points for homography transformation. "
            f"Got {len(source_points)}."
        )

    if len(source_points) != 4:
        raise ValueError(
            f"Need exactly 4 points for homography transformation. "
            f"Got {len(source_points)}."
        )

    return HomographyTransformer(source_points, target_points)


def main(camera_id: int, width: int, height: int, rotate: bool = False) -> None:
    """
    Main function to capture and process camera frames.
    """

    pf = Playfield(1000, 500)

    # Load calibration points
    pf_to_pixel = load_transformer("cal_table.json", "cal_projector.json")

    cam_to_pf = load_transformer("cal_cam.json", "cal_table.json")

    # print(pf_to_pixel.map_point(Point2Da(100, 200)))

    try:
        camera = Camera(camera_id, width, height, rotate)
        image = cv2.imread("testimg.png")
        while True:
            frame = camera.get_frame()
            # frame = image.copy()

            cp = FrameProcessor(frame)

            # cv2.imshow('Codes', frame)
            cv2.imshow('Hands', cp.get_marked_frame())
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
        "--projector", action="store_true", help="Calibrate Projector")
    parser.add_argument(
        "--camera", action="store_true", help="Calibrate Camera")
    parser.add_argument(
        "--rotate", action="store_true", help="Rotate camera frame")
    args = parser.parse_args()

    mqtt = MqttHandler(os.getenv("MQTT_BROKER"),
                       int(os.getenv("MQTT_PORT")),
                       os.getenv("MQTT_TOPIC"),
                       os.getenv("MQTT_USER"),
                       os.getenv("MQTT_PASSWORD"))

    if args.projector:
        calibrate_projector(mqtt)
        exit(1)

    if args.camera:
        calibrate_camera(Camera(args.camera_id, args.width,
                         args.height, args.rotate), "cal_cam.json")
        exit(1)

    main(args.camera_id, args.width, args.height, args.rotate)
