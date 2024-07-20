import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from pyppeteer import launch


class RenderRequest(BaseModel):
    html_src: str
    css_src: str


class RenderResponse(BaseModel):
    image_path: str


class Renderer:
    def __init__(self, max_concurrent_renders: int = 10):
        self.browser = None
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrent_renders)

    async def init_browser(self):
        async with self.lock:
            if self.browser is None:
                self.browser = await launch()

    async def html_to_image(
        self, html_content: str, css_content: str, output_path: str
    ):
        async with self.semaphore:  # Use semaphore to limit concurrency
            page = await self.browser.newPage()
            try:
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
                await page.setJavaScriptEnabled(False)
                await page.setViewport({"width": 500, "height": 500})
                await page.setContent(src)
                await page.screenshot({"path": output_path})
            finally:
                await page.close()


renderer = Renderer()
render_router = APIRouter()


@render_router.post("/render")
async def render(request: RenderRequest) -> RenderResponse:
    html_content = request.html_src
    css_content = request.css_src

    output_path = f"rendered_{uuid.uuid4()}.png"

    try:
        await renderer.html_to_image(html_content, css_content, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to render image: " + str(e))

    return RenderResponse(image_path=output_path)


@asynccontextmanager
async def lifespan(app):
    await renderer.init_browser()
    try:
        yield
    finally:
        if renderer.browser is not None:
            await renderer.browser.close()
