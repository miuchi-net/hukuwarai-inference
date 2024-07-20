import base64
import io

import numpy as np
import uvicorn
from fastapi import FastAPI
from PIL import Image as PILImage
from pydantic import BaseModel

from imgsim import ImageSim
from models import MSE, PtPretrainedModel, Zero


class Image(BaseModel):
    data: str


class SimilarityRequest(BaseModel):
    img1: Image
    img2: Image
    model_name: str


app = FastAPI()


@app.post("/similarity")
async def similarity(request: SimilarityRequest):
    img1_data = base64.b64decode(request.img1.data)
    img2_data = base64.b64decode(request.img2.data)

    img1 = PILImage.open(io.BytesIO(img1_data))
    img2 = PILImage.open(io.BytesIO(img2_data))

    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")

    img1 = img1.resize((500, 500))
    img2 = img2.resize((500, 500))

    print("img1 shape:", np.array(img1).shape)
    print("img2 shape:", np.array(img2).shape)

    img1 = np.array(img1)
    img2 = np.array(img2)

    if request.model_name == "mse":
        model = MSE()
    elif request.model_name == "zero":
        model = Zero()
    else:
        model = PtPretrainedModel(request.model_name)

    imgsim = ImageSim(img1, img2, model)
    return {"similarity": imgsim.calculate()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
