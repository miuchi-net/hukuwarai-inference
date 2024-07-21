import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from pyppeteer import launch


class RenderRequest(BaseModel):
    html_src: str


class RenderResponse(BaseModel):
    image_url: str


class Renderer:
    def __init__(self, max_concurrent_renders: int = 10):
        self.browser = None
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrent_renders)

    async def init_browser(self):
        async with self.lock:
            if self.browser is None:
                self.browser = await launch(args=["--no-sandbox"])

    async def html_to_image(
        self, html_content: str, output_path: str
    ):
        async with self.semaphore:
            page = await self.browser.newPage()
            try:
                src = f"""
                <html>
                <body>
                    {html_content}
                </body>
                </html>
                """
                await page.setJavaScriptEnabled(False)
                await page.setOfflineMode(True)
                await page.setViewport({"width": 500, "height": 500})
                await page.setContent(src)
                await page.screenshot({"path": output_path})
            finally:
                await page.close()

    async def boundingbox(self, html_content: str, output_path: str):
        async with self.semaphore:
            page = await self.browser.newPage()
            try:
                src = f"""
                <html>
                <body>
                    {html_content}
                </body>
                </html>
                """
                await page.setJavaScriptEnabled(False)
                await page.setOfflineMode(True)
                await page.setViewport({"width": 500, "height": 500})
                await page.setContent(src)
                # body 以下の全ての要素のbounding boxを取得する
                elements = await page.querySelectorAll("body *")
                print(f"--- Found {len(elements)} elements ---")
                for element in elements:
                    box = await element.boundingBox()
                    print("Box:", box)
                    if box is None:
                        continue
                    # bounding boxを描画して、元の div を削除
                    await page.evaluate(
                        """
                        (box) => {
                            const div = document.createElement('div');
                            div.style.position = 'absolute';
                            div.style.border = '1px solid red';
                            div.style.left = box.x + 'px';
                            div.style.top = box.y + 'px';
                            div.style.width = box.width + 'px';
                            div.style.height = box.height + 'px';
                            document.body.appendChild(div);
                        }
                        """,
                        box,
                    )

                # element を削除 (ここの for を分ける必要があることに注意)
                for element in elements:
                    await page.evaluate(
                        """
                        (element) => {
                            element.remove();
                        }
                        """,
                        element,
                    )

                await page.screenshot({"path": output_path})

            finally:
                await page.close()


renderer = Renderer()
render_router = APIRouter()


@render_router.post("/render")
async def render(request: RenderRequest) -> RenderResponse:
    html_content = request.html_src

    output_path = f"/static/rendered_{uuid.uuid4()}.png"

    try:
        await renderer.html_to_image(html_content, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to render image: " + str(e))

    return RenderResponse(image_path=output_path)


@render_router.post("/boudingbox")
async def boundingbox(request: RenderRequest) -> RenderResponse:
    html_content = request.html_src
    
    output_path = f"/static/rendered_{uuid.uuid4()}.png"

    try:
        await renderer.boundingbox(html_content, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to render image: " + str(e))

    return RenderResponse(image_path=output_path)
