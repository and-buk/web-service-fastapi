from datetime import datetime
from typing import List

import pytest
from pydantic import BaseModel


class Object(BaseModel):
    object_name: str
    created_at: datetime


class PostResponce(BaseModel):
    objects: List[Object]


@pytest.mark.anyio
class TestPostRoute:
    async def test_pull_jpeg_image(self, test_images_jpeg, async_client):
        test_files = test_images_jpeg
        files = {
            "files": ("test_file", open(test_files[0], "rb"), "image/jpeg")
        }
        response = await async_client.post("/frames/", files=files)
        assert response.status_code == 201
        assert PostResponce.parse_obj(response.json())

    async def test_pull_png_image(self, test_image_png, async_client):
        test_file = test_image_png
        files = {"files": ("test_file", open(test_file, "rb"), "image/png")}
        response = await async_client.post("/frames/", files=files)
        assert response.status_code == 400
