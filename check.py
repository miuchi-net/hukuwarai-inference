import base64
import io
import uuid

import requests
from PIL import Image
import argparse


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def similarity(image_path1, image_path2, model_name):
    url = "http://127.0.0.1:8000/similarity"
    img1_base64 = image_to_base64(image_path1)
    img2_base64 = image_to_base64(image_path2)

    payload = {
        "img1": {"data": img1_base64},
        "img2": {"data": img2_base64},
        "model_name": model_name,
    }

    response = requests.post(url, json=payload)
    return response.json()


def render(html_content, css_content):
    url = "http://127.0.0.1:8000/render"

    payload = {
        "html_src": html_content,
        "css_src": css_content,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to render image: " + response.text)


def palette(image_path, max_colors):
    url = "http://127.0.0.1:8000/palette"

    payload = {
        "img": {"data": image_to_base64(image_path)},
        "max_colors": max_colors,
    }

    response = requests.post(url, json=payload)
    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image similarity, HTML to image conversion, and color picker")
    parser.add_argument("action", type=str, choices=["similarity", "render", "palette"], help="Action to perform")
    parser.add_argument("args", nargs="*", help="Arguments for the action")
    args = parser.parse_args()

    if args.action == "similarity":
        if len(args.args) != 3:
            print("Usage for compare: check.py similarity <image1> <image2> <model_name>")
        else:
            image1, image2, model_name = args.args
            result = similarity(image1, image2, model_name)
            print("result:", result)
    elif args.action == "render":
        if len(args.args) < 1 or len(args.args) > 2:
            print("Usage for render: check.py render <html_content> [css_content]")
        else:
            html_path = args.args[0]
            with open(html_path, "r") as f:
                html_content = f.read()

            css_content = ""
            if len(args.args) == 2:
                css_path = args.args[1]
                with open(css_path, "r") as f:
                    css_content = f.read()

            result = render(html_content, css_content)
            print("result:", result)
    elif args.action == "palette":
        if len(args.args) != 2:
            print("Usage for palette: check.py color_picker <image> <max_colors>")
        else:
            image_path, max_colors = args.args
            result = palette(image_path, int(max_colors))
            print("result:", result)
            colors = result["palette"]
            img = Image.new("RGB", (100 * len(colors), 100))
            for i, color in enumerate(colors):
                img.paste(Image.new("RGB", (100, 100), color), (100 * i, 0))

            img.save(f"palette_{uuid.uuid4()}.png")
            