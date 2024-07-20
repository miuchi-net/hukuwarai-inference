import numpy as np
import torch
from torchvision import transforms
from torchvision.transforms import Compose


class SimilalityCalculator:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def calculate(self, img1: np.ndarray, img2: np.ndarray) -> float:
        raise NotImplementedError()


class ImageSim:
    def __init__(
        self, img1: np.ndarray, img2: np.ndarray, calculator: SimilalityCalculator
    ):
        if not self._vaidate_img(img1, img2):
            # raise ValueError("Images are not valid")
            return 0

        self.img1 = self._preprocess(img1)
        self.img2 = self._preprocess(img2)

        self.model = calculator

    def _vaidate_img(self, img1, img2) -> bool:
        checklist = [
            (
                lambda img1, img2: isinstance(img1, np.ndarray)
                and isinstance(img2, np.ndarray),
                "img1 and img2 must be numpy.ndarray",
            ),
            (
                lambda img1, img2: img1.shape == img2.shape,
                "img1 and img2 must have the same shape",
            ),
        ]

        for check, msg in checklist:
            if not check(img1, img2):
                print(msg)
                return False

        return True

    def _preprocess(self, img: np.ndarray) -> torch.Tensor:
        preprocess = Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        img = preprocess(img)
        img = img.unsqueeze(0)
        return img

    def calculate(self) -> float:
        return self.model.calculate(self.img1, self.img2)
