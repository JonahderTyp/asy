import argparse
import json
import os
from time import sleep

import cv2
import numpy as np
import requests
from dotenv import load_dotenv

from .calibrator import calibrate_projector
from .camera import Camera
from .camera.calibrate import calibrate_camera
from .datastructures import Circle, Form, Playfield, Point2Da, Polygon, Text
from .hand_tracker import HandTracker
from .mqtt_handler import MqttHandler
from .pcb_tracker import FrameProcessor as PCB_FrameProcessor
from .transformer import HomographyTransformer


class PCB_Manager:
    """
    A class to manage PCB object placement
    """

    def __init__(self):
        self._steps = [
            None,  # Step 0: Initial state
            Polygon((255, 255, 255), [Point2Da(85, 50), Point2Da(
                85, 85), Point2Da(120, 85), Point2Da(120, 50)]),
            Circle((255, 255, 255), Point2Da(160, 35), 5),
            Circle((255, 255, 255), Point2Da(160, 105), 5),
        ]

        self._current_step = 0

    def get_current_step(self) -> Form | None:
        """
        Get the current step in the PCB placement process.
        :return: The current step as a Form object or None if no step is set.
        """
        return self._steps[self._current_step]

    def get_step(self, step: int) -> Form | None:
        if 0 <= step < len(self._steps):
            return self._steps[step]
        return None

    def next_step(self) -> None:
        """
        Move to the next step in the PCB placement process. Go back to the first step if at the last step.
        """
        self._current_step = (self._current_step + 1) % len(self._steps)

    def back_step(self) -> None:
        """
        Move to the previous step in the PCB placement process. Go to the last step if at the first step.
        """
        self._current_step = (self._current_step - 1) % len(self._steps)


class Schublade:
    """
    A class to represent a drawer with a name and an ID.
    """

    def __init__(self, id: int, url: str):
        self.id = id
        self.url = url
        self._state = None  # None means unknown, True means open, False means closed
        self.set_state(False)  # Initialize the drawer to closed state

    def set_state(self, state: bool):
        """
        Set the state of the drawer.
        :param state: True if the drawer is open, False if closed.
        """
        if state != self._state:
            self._state = state

            try:
                requests.get(
                    self.url + f"move?servo={self.id}&place={170 if state else 10}")
            except requests.RequestException as e:
                print(f"Error setting state for drawer {self.id}: {e}")

    def __repr__(self):
        return f"Schublade(name={self.name}, id={self.id})"


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

    pcb_pf = Playfield(210, 115)  # A4 size in mm
    # pcb_tl: Point2Da | None = Point2Da(400, 400)
    # pcb_tr: Point2Da | None = Point2Da(600, 400)
    # pcb_bl: Point2Da | None = Point2Da(400, 600)
    # pcb_br: Point2Da | None = Point2Da(600, 800)
    pcb_tl: Point2Da | None = None
    pcb_tr: Point2Da | None = None
    pcb_bl: Point2Da | None = None
    pcb_br: Point2Da | None = None

    s0 = Schublade(0, "http://172.16.1.145/")
    s1 = Schublade(1, "http://172.16.1.145/")
    s2 = Schublade(2, "http://172.16.1.145/")

    stepper = PCB_Manager()

    projector_pf = Playfield(os.getenv("PROJECTOR_WIDTH"),
                             os.getenv("PROJECTOR_HEIGHT"))

    # Load calibration points
    print("Loading pf_to_pixel points...")
    pf_to_pixel = load_transformer("cal_table.json", "cal_projector.json")
    # pf_to_pixel = load_transformer("cal_projector.json", "cal_table.json")

    print("Loading cam_to_pf points...")
    cam_to_pf = load_transformer("cal_cam.json", "cal_table.json")

    # print(pf_to_pixel.map_point(Point2Da(100, 200)))

    # print(cam_to_pf.map_point(Point2Da(640, 402)))

    print("PF to Pixel Transformer:")
    print(pf_to_pixel.map_point(Point2Da(800, 500)))

    last_hand_in_zone_1 = None
    last_hand_in_zone_2 = None

    try:
        camera = Camera(camera_id, width, height, rotate)
        # image = cv2.resize(cv2.imread("testimg.png"), [800, 600])
        ht = HandTracker()
        while True:
            pf.clear()

            # Clear Framebuffers
            for _ in range(0):
                camera.get_frame()

            frame = camera.get_frame()
            # frame = image.copy()

            cp = PCB_FrameProcessor(frame)

            hand_in_danger = False
            want_to_next_step = False
            want_to_last_step = False
            hand_in_zone_1 = False
            hand_in_zone_2 = False

            match stepper._current_step:
                case 1:
                    s0.set_state(True)
                    s1.set_state(False)
                    s2.set_state(False)
                case 2:
                    s0.set_state(False)
                    s1.set_state(True)
                    s2.set_state(False)
                case 3:
                    s0.set_state(False)
                    s1.set_state(False)
                    s2.set_state(True)
                case _:
                    s0.set_state(False)
                    s1.set_state(False)
                    s2.set_state(False)

            if True:
                # print(cp.codes)
                ids = list(cp.codes.keys())
                ids.sort()
                if all(x in ids for x in [10, 11, 12, 13]):
                    # print("Found PCB corners")
                    pcb_tl = cam_to_pf.map_point(cp.codes[11].center)
                    pcb_tr = cam_to_pf.map_point(cp.codes[10].center)
                    pcb_bl = cam_to_pf.map_point(cp.codes[12].center)
                    pcb_br = cam_to_pf.map_point(cp.codes[13].center)
                    # print(
                    #     f"PCB corners: {pcb_tl}, {pcb_tr}, {pcb_bl}, {pcb_br}")
                    # print(
                    #     f"PCB Type: {type(pcb_tl)} {type(pcb_tr)} {type(pcb_bl)} {type(pcb_br)}")

                if all(x in ids for x in [20, 21, 22, 23]):
                    pcb_tl = cam_to_pf.map_point(cp.codes[20])
                    pcb_tr = cam_to_pf.map_point(cp.codes[21])
                    pcb_bl = cam_to_pf.map_point(cp.codes[22])
                    pcb_br = cam_to_pf.map_point(cp.codes[23])

            hands = ht.detect_hands(frame)
            handpos = ht.get_hand_positions()
            mapped_hands = cam_to_pf.map_object(handpos)
            for nrh, hand in enumerate(mapped_hands):
                if len(hand) < 4:
                    continue
                point: Point2Da
                for i, point in enumerate(hand):

                    if point.y < 200 and point.x < 800 and point.x > 400:
                        hand_in_danger = True

                    if point.y > 50 and point.y < 100 \
                            and point.x > 1000 and point.x < 1050:
                        hand_in_zone_1 = True

                    if point.y > 50 and point.y < 100 \
                            and point.x > 900 and point.x < 950:
                        hand_in_zone_2 = True

            pf.put_form(
                11, Polygon(
                    color=(0, 255, 255),
                    points=[
                        Point2Da(900, 50),
                        Point2Da(950, 50),
                        Point2Da(950, 100),
                        Point2Da(900, 100),
                    ]
                )
            )

            pf.put_form(
                12, Text(
                    color=(0, 255, 255),
                    text="Back",
                    position=Point2Da(905, 75),
                    size=12
                )
            )

            pf.put_form(
                13, Polygon(
                    color=(0, 255, 0),
                    points=[
                        Point2Da(1000, 50),
                        Point2Da(1050, 50),
                        Point2Da(1050, 100),
                        Point2Da(1000, 100),
                    ]
                )
            )

            pf.put_form(
                14, Text(
                    color=(0, 255, 0),
                    text="Weiter",
                    position=Point2Da(1005, 75),
                    size=12
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
                    5005, stepper.get_current_step())
                # print(pcb_pf._forms)
                pcb_pf.transform(tr, pf)

            # cv2.imshow('Codes', frame)

            if hand_in_zone_1 != last_hand_in_zone_1 and hand_in_zone_1:
                want_to_next_step = True

            if hand_in_zone_2 != last_hand_in_zone_2 and hand_in_zone_2:
                want_to_last_step = True

            if hand_in_danger and (hand_in_zone_1 or hand_in_zone_2):
                pf.put_form(
                    10, Polygon(
                        color=(0, 0, 255),
                        points=[
                            Point2Da(400, 0),
                            Point2Da(400, 200),
                            Point2Da(800, 200),
                            Point2Da(800, 0),
                        ]
                    )
                )
            else:
                pf.put_form(
                    10, None)

            if want_to_next_step and not hand_in_danger:
                stepper.next_step()
                print(f"Next step: {stepper.get_current_step()}")
                want_to_next_step = False

            if want_to_last_step and not hand_in_danger:
                stepper.back_step()
                want_to_last_step = False

            last_hand_in_zone_1 = hand_in_zone_1
            last_hand_in_zone_2 = hand_in_zone_2

            projector_pf.clear()
            pf.transform(pf_to_pixel,
                         projector_pf)

            cv2.imshow('Playfield', pf.render())
            cv2.imshow('Projector', projector_pf.render(
                offset=Point2Da(0, 0)))
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
        projector_pf.clear()
        mqtt.send(projector_pf.to_json())
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
