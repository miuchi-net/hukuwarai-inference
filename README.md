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

```json
{
  "similarity": 0.0
}
```







