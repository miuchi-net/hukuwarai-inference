import uvicorn
from fastapi import FastAPI

from routers.render_router import render_router
from routers.similarity_router import similarity_router
from routers.palette_router import palette_router
from routers.render_router import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(render_router)
app.include_router(similarity_router)
app.include_router(palette_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
