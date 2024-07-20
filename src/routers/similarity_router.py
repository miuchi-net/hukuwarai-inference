from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import io
import numpy as np
from PIL import Image as PILImage
from models import MSE, Zero, PtPretrainedModel
from imgsim import ImageSim

class Image(BaseModel):
    data: str

class SimilarityRequest(BaseModel):
    img1: Image
    img2: Image
    model_name: str

class SimilarityResponse(BaseModel):
    similarity: float

similarity_router = APIRouter()

@similarity_router.post("/similarity")
async def similarity(request: SimilarityRequest) -> SimilarityResponse:
    img1_data = base64.b64decode(request.img1.data)
    img2_data = base64.b64decode(request.img2.data)

    img1 = PILImage.open(io.BytesIO(img1_data))
    img2 = PILImage.open(io.BytesIO(img2_data))

    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")

    img1 = img1.resize((500, 500))
    img2 = img2.resize((500, 500))

    img1 = np.array(img1)
    img2 = np.array(img2)

    if request.model_name == "mse":
        model = MSE()
    elif request.model_name == "zero":
        model = Zero()
    else:
        model = PtPretrainedModel(request.model_name)

    imgsim = ImageSim(img1, img2, model)

    similarity = imgsim.calculate()

    return SimilarityResponse(similarity=similarity)
