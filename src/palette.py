import numpy as np
from sklearn.cluster import KMeans

from config import Config


class PaletteSolver:
    def __init__(self, img: np.ndarray, max_colors: int):
        if not self._validate_img(img):
            return

        self.img = img
        self.max_colors = max_colors

    def solve(self):
        img = self.img
        img = img.reshape(-1, 3)
        # Config.colorpicker_threshold を下回るか 、max_colors に達するまでクラスタリングを行う
        for n_clusters in range(1, self.max_colors + 1):
            kmeans = KMeans(
                n_clusters=n_clusters, random_state=Config.random_state
            ).fit(img)
            labels = kmeans.labels_
            cluster_centers = kmeans.cluster_centers_
            unique_labels = np.unique(labels)
            if len(unique_labels) == self.max_colors:
                break

            score = -kmeans.score(img) / len(img)
            print(f"n_clusters: {n_clusters}, score: {score}")
            if score < Config.colorpicker_threshold:
                break

        return [self._rgb_to_hex(color) for color in cluster_centers]

    def _rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*[int(c) for c in rgb])


    # TODO: Implement Error Handling
    def _validate_img(self, img):
        checklist = [
            (
                lambda img: isinstance(img, np.ndarray),
                "img must be numpy.ndarray",
            ),
        ]

        for check, msg in checklist:
            if not check(img):
                print(msg)
                return False

        return True
