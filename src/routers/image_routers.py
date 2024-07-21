from io import BytesIO

import numpy as np
import requests
from fastapi import APIRouter, HTTPException
from PIL import Image as PILImage
from pydantic import BaseModel

from imgsim import ImageSim
from models import MSE, PtPretrainedModel, Zero
from palette import PaletteSolver


class Image(BaseModel):
    url: str


class SimilarityRequest(BaseModel):
    img1: Image
    img2: Image
    model_name: str


class PelleteRequest(BaseModel):
    img: Image
    max_colors: int


class PelleteResponse(BaseModel):
    palette: list
    n_colors: int


class SimilarityResponse(BaseModel):
    similarity: float


image_router = APIRouter()


def _preprocess(img: PILImage.Image) -> np.ndarray:
    img = img.convert("RGB")
    img = img.resize((500, 500))
    img = np.array(img)
    return img


@image_router.post("/similarity")
async def similarity(request: SimilarityRequest) -> SimilarityResponse:
    input_url = request.img1.url
    target_url = request.img2.url
    
    input_data_local_path = './static/' + input_url.split('/')[-1]

    input_image = PILImage.open(input_data_local_path)
    target_image = PILImage.open(BytesIO(requests.get(target_url).content))

    input_image = _preprocess(input_image)
    target_image = _preprocess(target_image)
    
    if request.model_name == "mse":
        model = MSE()
    elif request.model_name == "zero":
        model = Zero()
    else:
        model = PtPretrainedModel(request.model_name)

    imgsim = ImageSim(input_image, target_image, model)

    similarity = imgsim.calculate()

    return SimilarityResponse(similarity=similarity)


@image_router.post("/palette")
async def palette(request: PelleteRequest) -> PelleteResponse:
    img_url = request.img.url

    img_data = requests.get(img_url).content

    if not img_data:
        raise HTTPException(status_code=404, detail="Image not found")

    img_data = PILImage.open(BytesIO(img_data))

    img = _preprocess(img_data)

    max_colors = request.max_colors

    solver = PaletteSolver(img, max_colors)

    palette = solver.solve()

    return PelleteResponse(palette=palette, n_colors=len(palette))
