import numpy as np
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
    image1_local_path = './static/' + request.img1.url.split("/")[-1]
    image2_local_path = './static/' + request.img2.url.split("/")[-1]

    img1_data = PILImage.open(image1_local_path)
    img2_data = PILImage.open(image2_local_path)

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
    image_local_path = './static/' + request.img.url.split("/")[-1]

    img_data = PILImage.open(image_local_path)

    img = _preprocess(img_data)

    max_colors = request.max_colors

    solver = PaletteSolver(img, max_colors)

    palette = solver.solve()

    return PelleteResponse(palette=palette, n_colors=len(palette))
