from datetime import datetime
from typing import List

import pytest
from pydantic import BaseModel, HttpUrl


class ObjectGetInfo(BaseModel):
    object_name: str
    download_url: HttpUrl
    registration_date: datetime


class GetResponce(BaseModel):
    objects: List[ObjectGetInfo]


@pytest.mark.anyio
class TestGetRoute:
    async def test_get_images(self, async_client, create_test_objects):
        bucket_name = create_test_objects
        response = await async_client.get(f"/frames/{bucket_name[1]}")
        assert response.status_code == 200
        assert GetResponce.parse_obj(response.json())

    async def test_get_images_from_nonexistent_bucket(self, async_client):
        response = await async_client.get("/frames/2022-06-30")
        assert response.status_code == 404

    @pytest.mark.parametrize("path_param", ["aaa", 123])
    async def test_get_images_with_invalid_path_params(
        self, async_client, path_param
    ):
        response = await async_client.get("/frames/path_param")
        assert response.status_code == 422
