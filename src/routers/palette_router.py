from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import io
import numpy as np
from PIL import Image as PILImage
from palette import PaletteSolver

class Image(BaseModel):
    data: str

class PelleteRequest(BaseModel):
    img: Image
    max_colors: int

class PelleteResponse(BaseModel):
    palette: list
    n_colors: int

palette_router = APIRouter()

@palette_router.post("/palette")
async def palette(request: PelleteRequest) -> PelleteResponse:
    img_data = base64.b64decode(request.img.data)
    img = PILImage.open(io.BytesIO(img_data))
    img = img.convert("RGB")
    img = img.resize((500, 500))
    img = np.array(img)

    max_colors = request.max_colors

    solver = PaletteSolver(img, max_colors)

    palette = solver.solve()

    return PelleteResponse(palette=palette, n_colors=len(palette))
