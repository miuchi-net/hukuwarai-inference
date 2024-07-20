import base64
import io
import uuid

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from PIL import Image as PILImage
from pydantic import BaseModel
from pyppeteer import launch

from imgsim import ImageSim
from models import MSE, PtPretrainedModel, Zero


class Image(BaseModel):
    data: str


class SimilarityRequest(BaseModel):
    img1: Image
    img2: Image
    model_name: str

class SimilarityResponse(BaseModel):
    similarity: float


class RenderRequest(BaseModel):
    html_src: str
    css_src: str

class RenderResponse(BaseModel):
    image_path: str

app = FastAPI()

async def html_to_image(html_content: str, css_content: str, output_path: str):
    browser = await launch()
    page = await browser.newPage()
    src = f"""
    <html>
    <head>
        <style>{css_content}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    await page.setContent(src)
    await page.screenshot({"path": output_path, "fullPage": True})
    await browser.close()


@app.post("/render")
async def render(request: RenderRequest) -> RenderResponse:
    html_content = request.html_src
    css_content = request.css_src

    output_path = f"rendered_{uuid.uuid4()}.png"

    try:
        await html_to_image(html_content, css_content, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to render image: " + str(e))

    return RenderResponse(image_path=output_path)


@app.post("/similarity")
async def similarity(request: SimilarityRequest) -> SimilarityResponse:
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
    
    similarity = imgsim.calculate()

    return SimilarityResponse(similarity=similarity)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
