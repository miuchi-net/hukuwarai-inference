import argparse
import base64
import concurrent.futures
import io
import time
import uuid

import requests
from PIL import Image


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def similarity(image_path1, image_path2, model_name):
    url = "http://127.0.0.1:8000/similarity"
    # img1_base64 = image_to_base64(image_path1)
    # img2_base64 = image_to_base64(image_path2)

    payload = {
        "img1": {"url": image_path1},
        "img2": {"url": image_path2},
        "model_name": model_name,
    }

    response = requests.post(url, json=payload)
    return response.json()


def render(html_content):
    url = "http://127.0.0.1:8000/render"

    payload = {
        "html_src": html_content,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to render image: " + response.text)


def boundingbox(html_content):
    url = "http://127.0.0.1:8000/boudingbox"

    payload = {
        "html_src": html_content,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to render image: " + response.text)


def palette(image_path, max_colors):
    url = "http://127.0.0.1:8000/palette"

    payload = {
        "img": {
            "url": image_path,
        },
        "max_colors": max_colors,
    }

    response = requests.post(url, json=payload)
    return response.json()


def run_task(action, args, index):
    start_time = time.time()

    if action == "similarity":
        if len(args) != 3:
            result = (
                "Usage for compare: check.py similarity <image1> <image2> <model_name>"
            )
        else:
            image1, image2, model_name = args
            result = similarity(image1, image2, model_name)
    elif action == "render":
        if len(args) != 1:
            result = "Usage for render: check.py render <html_content>"
        else:
            html_path = args[0]
            with open(html_path, "r") as f:
                html_content = f.read()

            result = render(html_content)

    elif action == "boundingbox":
        if len(args) != 1:
            result = "Usage for boundingbox: check.py boundingbox <html_content>"
        else:
            html_path = args[0]
            with open(html_path, "r") as f:
                html_content = f.read()

            result = boundingbox(html_content)

    elif action == "palette":
        if len(args) != 2:
            result = "Usage for palette: check.py color_picker <image> <max_colors>"
        else:
            image, n_color = args
            result = palette(image, n_color)

    else:
        raise ValueError("Invalid action")

    return result, time.time() - start_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Image similarity, HTML to image conversion, and color picker"
    )
    parser.add_argument(
        "action",
        type=str,
        choices=["similarity", "render", "boundingbox", "palette"],
        help="Action to perform",
    )
    parser.add_argument("args", nargs="*", help="Arguments for the action")

    args = parser.parse_args()

    start_time = time.time()

    N_PROCESSES = 1
    N_PARALLEL = 1

    with concurrent.futures.ProcessPoolExecutor(max_workers=N_PROCESSES) as executor:
        futures = [
            executor.submit(run_task, args.action, args.args, i)
            for i in range(N_PARALLEL)
        ]
        for future in concurrent.futures.as_completed(futures):
            result, elapsed_time = future.result()
            print(f"Result: {result}")
            print(f"Elapsed time: {elapsed_time:.2f} seconds")
            print()

    print(f"Total elapsed time: {time.time() - start_time:.2f} seconds")


