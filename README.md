# hukuwarai-inference

(Not Production Ready)

## Usage

```bash
$ pipenv install
$ pipenv run python main.py
```

- `http://localhost:8000/`
- `http://localhost:8000/docs`: Swagger 

## Endpoints


### `POST /similarity`

Calculate similarity between two images.

#### Request

```json
{
  "img1": {
    "data": "string"
  },
  "img2": {
    "data": "string"
  },
  "model_name": "string"
}
```

- `img1`: Image data. base64 encoded any image.
- `img2`: Image data. base64 encoded any image.
- `model_name`: Model name. Models in https://github.com/huggingface/pytorch-image-models, `"mse"`, `"zero"` are available. `"mse"` is Mean Squared Error, `"zero"` is always return 0.0. (for testing)

#### Response

Similarity between two images.

It is guaranteed that the similarity is between 0.0 and 1.0.


```json
{
  "similarity": 0.0
}
```


### `POST /render`

Render image from HTML and CSS.

#### Request

```json
{
  "html_src": "string",
  "css_src": "string"
}
```

- `html_src`: HTML source.
- `css_src`: CSS source.


#### Response



```json
{
  "image_path": "string"
}
```

- `image_path`: Path to rendered image.


## Chcker

```bash
➤ python3 check.py similarity target.png dog.jpg resnet18
result: {'similarity': 0.3008711338043213}
➤ python3 check.py render example.html example.css
result: {'image_path': 'rendered_2066ad6b-8f62-4e17-bfb4-5e2ffc6cb7b5.png'}
```

`rendered_2066ad6b-8f62-4e17-bfb4-5e2ffc6cb7b5.png`

![rendered_2066ad6b-8f62-4e17-bfb4-5e2ffc6cb7b5.png](rendered_2066ad6b-8f62-4e17-bfb4-5e2ffc6cb7b5.png)