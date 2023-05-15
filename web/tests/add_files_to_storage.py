from typing import List

import pytest
from pydantic import BaseModel


class PostRequest(BaseModel):
    file_name: str
    object_name: str


class PostResponce(BaseModel):
    user: str
    user_objects: List[PostRequest]


@pytest.mark.anyio
class TestPostRoute:
    async def test_pull_jpeg_image(self, test_images_jpeg, async_client, user_auth):
        test_files = test_images_jpeg
        access_token = user_auth["access_token"]
        files = {"files": ("test_file", open(test_files[0], "rb"), "image/jpeg")}
        response = await async_client.post(
            "frames/",
            headers={"Authorization": f"Bearer {access_token}"},
            files=files,
        )
        assert response.status_code == 201
        assert PostResponce.parse_obj(response.json())

    async def test_pull_png_image(self, test_image_png, async_client, user_auth):
        test_file = test_image_png
        access_token = user_auth["access_token"]
        files = {"files": ("test_file", open(test_file, "rb"), "image/png")}
        response = await async_client.post(
            "/frames/",
            headers={"Authorization": f"Bearer {access_token}"},
            files=files,
        )
        assert response.status_code == 400
