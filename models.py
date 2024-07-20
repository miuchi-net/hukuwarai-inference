import torch
from timm import create_model

from imgsim import SimilalityCalculator


class PtPretrainedModel(SimilalityCalculator):
    def __init__(self, model_name: str):
        self.model = create_model(model_name, pretrained=True, num_classes=0)
        self.model.eval()

    def calculate(self, img1: torch.Tensor, img2: torch.Tensor) -> float:
        with torch.no_grad():
            feat1 = self.model(img1)
            feat2 = self.model(img2)

            return torch.nn.functional.cosine_similarity(feat1, feat2).item()


class MSE(SimilalityCalculator):
    def __init__(self):
        pass

    def calculate(self, img1: torch.Tensor, img2: torch.Tensor) -> float:
        return torch.nn.functional.mse_loss(img1, img2).item()


class Zero(SimilalityCalculator):
    def __init__(self):
        pass

    def calculate(self, img1: torch.Tensor, img2: torch.Tensor) -> float:
        return 0.0
