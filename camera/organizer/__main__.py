import argparse
import json
import os
from time import sleep

import cv2
import numpy as np
from dotenv import load_dotenv

from .calibrator import calibrate_projector
from .camera import Camera
from .camera.calibrate import calibrate_camera
from .datastructures import Circle, Playfield, Point2Da, Polygon
from .hand_tracker import HandTracker
from .mqtt_handler import MqttHandler
from .pcb_tracker import FrameProcessor as PCB_FrameProcessor
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

    print("Mapping points:")
    for i, (src, tgt) in enumerate(zip(source_points, target_points)):
        print(f"Point {i + 1}: Source {src} -> Target {tgt}")

    return HomographyTransformer(source_points, target_points)


def main(camera_id: int, width: int, height: int, rotate: bool = False) -> None:
    """
    Main function to capture and process camera frames.
    """

    pf = Playfield(1200, 600)

    pcb_pf = Playfield(297, 210)  # A4 size in mm
    # pcb_tl: Point2Da | None = Point2Da(400, 400)
    # pcb_tr: Point2Da | None = Point2Da(600, 400)
    # pcb_bl: Point2Da | None = Point2Da(400, 600)
    # pcb_br: Point2Da | None = Point2Da(600, 800)
    pcb_tl: Point2Da | None = None
    pcb_tr: Point2Da | None = None
    pcb_bl: Point2Da | None = None
    pcb_br: Point2Da | None = None

    projector_pf = Playfield(os.getenv("PROJECTOR_WIDTH"),
                             os.getenv("PROJECTOR_HEIGHT"))

    # Load calibration points
    print("Loading pf_to_pixel points...")
    pf_to_pixel = load_transformer("cal_table.json", "cal_projector.json")
    # pf_to_pixel = load_transformer("cal_projector.json", "cal_table.json")

    print("Loading cam_to_pf points...")
    cam_to_pf = load_transformer("cal_cam.json", "cal_table.json")

    # print(pf_to_pixel.map_point(Point2Da(100, 200)))

    try:
        camera = Camera(camera_id, width, height, rotate)
        image = cv2.resize(cv2.imread("testimg.png"), [800, 600])
        ht = HandTracker()
        while True:
            pf.clear()
            frame = camera.get_frame()
            # frame = image.copy()

            cp = PCB_FrameProcessor(frame)

            if True:
                # print(cp.codes)
                ids = list(cp.codes.keys())
                ids.sort()
                if all(x in ids for x in [10, 11, 12, 13]):
                    print("Found PCB corners")
                    pcb_tl = cp.codes[10].center
                    pcb_tr = cp.codes[11].center
                    pcb_bl = cp.codes[12].center
                    pcb_br = cp.codes[13].center
                    print(
                        f"PCB corners: {pcb_tl}, {pcb_tr}, {pcb_bl}, {pcb_br}")
                    print(
                        f"PCB Type: {type(pcb_tl)} {type(pcb_tr)} {type(pcb_bl)} {type(pcb_br)}")

                if all(x in ids for x in [20, 21, 22, 23]):
                    pcb_tl = cp.codes[20]
                    pcb_tr = cp.codes[21]
                    pcb_bl = cp.codes[22]
                    pcb_br = cp.codes[23]

                # pf.put_form(
                #     1,
                #     Circle(
                #         center=cam_to_pf.map_point(cp.center),
                #         radius=50,
                #         color=(255, 255, 0),
                #         fill=True
                #     )
                # )

            hands = ht.detect_hands(frame)
            mapped_hands = cam_to_pf.map_object(ht.get_hand_positions())
            for nrh, hand in enumerate(mapped_hands):
                if len(hand) < 4:
                    continue
                id = 100 * (nrh + 1)

                for i, point in enumerate(hand):
                    # Convert hand points to playfield coordinates
                    pf.put_form(
                        id + i,
                        Circle(
                            center=Point2Da(point.x, point.y),
                            radius=10,
                            color=(0, 255, 0)
                        )
                    )

            # If all PCB corners are detected, draw the PCB
            if type(pcb_tl) is Point2Da and type(pcb_tr) is Point2Da and \
                    type(pcb_bl) is Point2Da and type(pcb_br) is Point2Da:
                tr = HomographyTransformer(
                    [Point2Da(0, 0),
                     Point2Da(pcb_pf.width, 0),
                     Point2Da(0, pcb_pf.height),
                     Point2Da(pcb_pf.width, pcb_pf.height)],
                    [pcb_tl, pcb_tr, pcb_bl, pcb_br],
                )
                pcb_pf.clear()
                pcb_pf.put_form(
                    5000, Polygon(
                        points=[
                            Point2Da(0, 0),
                            Point2Da(0, 210),
                            Point2Da(297, 0),
                            Point2Da(297, 210)
                        ],
                        color=(0, 0, 255),
                    ))
                pcb_pf.put_form(
                    5001, Polygon(
                        points=[
                            Point2Da(0, 0),
                            Point2Da(297, 0),
                            Point2Da(297, 210),
                            Point2Da(0, 210),
                        ],
                        color=(0, 255, 255),
                    ))
                pcb_pf.transform(tr, pf)

            # cv2.imshow('Codes', frame)

            pf.transform(pf_to_pixel,
                         projector_pf)

            cv2.imshow('Playfield', pf.render())
            cv2.imshow('Projector', projector_pf.render())
            cv2.imshow('PCB', cp.get_marked_frame())
            cv2.imshow('Hands', hands)
            cv2.imshow('PCB_PF', pcb_pf.render())

            # Sende pf per MQTT
            mqtt.send(projector_pf.to_json())

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # except ValueError as e:
    #     print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
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
