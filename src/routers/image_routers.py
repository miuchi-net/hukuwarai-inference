import base64
import io
import os
from io import BytesIO

import boto3
import numpy as np
from fastapi import APIRouter, HTTPException
from PIL import Image
from PIL import Image as PILImage
from pydantic import BaseModel

from imgsim import ImageSim
from models import MSE, PtPretrainedModel, Zero
from palette import PaletteSolver


class S3Image(BaseModel):
    url: str


class SimilarityRequest(BaseModel):
    img1: S3Image
    img2: S3Image
    model_name: str


class PelleteRequest(BaseModel):
    img: S3Image
    max_colors: int


class PelleteResponse(BaseModel):
    palette: list
    n_colors: int


class SimilarityResponse(BaseModel):
    similarity: float


image_router = APIRouter()


class S3Loader:
    def __init__(self):
        pass

    def init_s3(self):
        self.s3 = boto3.client("s3")

    def load(self, url: str) -> Image:
        bucket = os.getenv("BUCKET")
        if bucket is None:
            raise ValueError("BUCKET environment variable is not set")
        img_data = self.s3.get_object(Bucket=bucket, Key=url)["Body"].read()
        image = Image.open(BytesIO(img_data))
        return image

    def close(self):
        pass


s3loader = S3Loader()


def _preprocess(img: Image) -> np.ndarray:
    img = img.convert("RGB")
    img = img.resize((500, 500))
    img = np.array(img)
    return img


@image_router.post("/similarity")
async def similarity(request: SimilarityRequest) -> SimilarityResponse:
    img1_data = s3loader.load(request.img1.url)
    img2_data = s3loader.load(request.img2.url)

    img1 = _preprocess(img1_data)
    img2 = _preprocess(img2_data)

    if request.model_name == "mse":
        model = MSE()
    elif request.model_name == "zero":
        model = Zero()
    else:
        model = PtPretrainedModel(request.model_name)

    imgsim = ImageSim(img1, img2, model)

    similarity = imgsim.calculate()

    return SimilarityResponse(similarity=similarity)


@image_router.post("/palette")
async def palette(request: PelleteRequest) -> PelleteResponse:
    img = s3loader.load(request.img.url)
    img = _preprocess(img)

    max_colors = request.max_colors

    solver = PaletteSolver(img, max_colors)

    palette = solver.solve()

    return PelleteResponse(palette=palette, n_colors=len(palette))
