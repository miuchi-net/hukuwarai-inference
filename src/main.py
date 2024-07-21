from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.render_router import render_router, renderer
from routers.image_routers import image_router

load_dotenv()


@asynccontextmanager
async def lifespan(app):
    await renderer.init_browser()
    try:
        yield
    finally:
        if renderer.browser is not None:
            await renderer.browser.close()


app = FastAPI(lifespan=lifespan)

app.include_router(render_router)
app.include_router(image_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
