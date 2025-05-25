import cv2


class Camera:
    def __init__(self, camera_id=0, width: int | None = None, height: int | None = None, rotate: bool = False):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.rotate = rotate
        self.cap = cv2.VideoCapture(camera_id)
        if width is not None and height is not None:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open camera {camera_id}")
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(
            f"Camera {camera_id} opened with resolution {self.width}x{self.height}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Can't receive frame")
        if self.rotate:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        return frame

    def release(self):
        self.cap.release()
