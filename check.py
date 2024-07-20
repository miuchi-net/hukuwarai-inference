import base64
import io

import requests
from PIL import Image


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def compare_images(image_path1, image_path2, model_name):
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


if __name__ == "__main__":
    image_path1 = "target.png"
    image_path2 = "dog.jpg"
    model_name = "resnet18"

    result = compare_images(image_path1, image_path2, model_name)
    print(result)
    print(result)
