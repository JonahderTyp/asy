import numpy as np


class HomographyTransformer:
    """
    Calibrates and applies a planar homography between two 2D point sets.

    Usage:
        transformer = HomographyTransformer(
            src_points=[[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
            dst_points=[[u1,v1], [u2,v2], [u3,v3], [u4,v4]]
        )
        mapped_point = transformer.map_point([x, y])
        mapped_points = transformer.map_batch([[x1,y1], [x2,y2]])
    """

    def __init__(self, src_points, dst_points):
        """
        Initialize with four or more corresponding 2D points.

        src_points: array-like of shape (N, 2) in the source coordinate system
        dst_points: array-like of shape (N, 2) in the destination coordinate system
        Requires at least 4 non-collinear points.
        """
        self.src = np.asarray(src_points, dtype=float)
        self.dst = np.asarray(dst_points, dtype=float)

        if self.src.shape != self.dst.shape or self.src.shape[0] < 4:
            raise ValueError(
                "Need at least four corresponding points of same shape.")
        self.H = self._compute_homography(self.src, self.dst)

    def _compute_homography(self, src_pts, dst_pts):
        """
        Compute homography matrix H that maps src_pts → dst_pts.
        """
        A, b = [], []
        for (u, v), (x, y) in zip(src_pts, dst_pts):
            A.append([u, v, 1, 0, 0, 0, -u * x, -v * x])
            b.append(x)
            A.append([0, 0, 0, u, v, 1, -u * y, -v * y])
            b.append(y)
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        # Solve for homography parameters
        h, *_ = np.linalg.lstsq(A, b, rcond=None)
        H = np.array([
            [h[0], h[1], h[2]],
            [h[3], h[4], h[5]],
            [h[6], h[7], 1.0]
        ])
        return H

    def map_point(self, point):
        """
        Apply homography to a single 2D point [u, v].
        Returns mapped [x, y].
        """
        u, v = point
        vec = np.array([u, v, 1.0])
        x_h, y_h, w_h = self.H.dot(vec)
        if np.isclose(w_h, 0):
            raise ValueError("Mapping resulted in infinite point (w≈0)")
        return np.array([x_h / w_h, y_h / w_h])

    def map_batch(self, points):
        """
        Apply homography to an array of shape (M,2) points.
        Returns an array of mapped points of shape (M,2).
        """
        pts = np.asarray(points, dtype=float)
        ones = np.ones((pts.shape[0], 1))
        hom_pts = np.hstack([pts, ones]) @ self.H.T
        hom_pts = hom_pts / hom_pts[:, 2][:, None]
        return hom_pts[:, :2]

    def __str__(self):
        return f"HomographyTransformer(src_points={self.src}, dst_points={self.dst})"

    def __repr__(self):
        return self.__str__()
