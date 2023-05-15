import logging
import os
from datetime import datetime

import pytest
from httpx import AsyncClient

from web.app.main import app

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
def test_image_png():
    file = os.path.join(ROOT_DIR, "test_data", "test_img_400.png")
    return file


@pytest.fixture(scope="module")
async def user_auth(async_client):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = await async_client.post(
        "/token",
        headers=headers,
        data={"username": "user", "password": "user", "scope": "user"},
    )
    return response.json()


@pytest.fixture()
def test_images_jpeg():
    file_1 = os.path.join(ROOT_DIR, "test_data", "test_img_200.jpeg")
    file_2 = os.path.join(ROOT_DIR, "test_data", "test_img_200_2.jpeg")
    return file_1, file_2


@pytest.fixture()
async def create_test_objects(test_images_jpeg, async_client, user_auth):
    test_files = test_images_jpeg
    access_token = user_auth["access_token"]
    multiple_files = [
        ("files", ("test_file", open(test_files[0], "rb"), "image/jpeg")),
        ("files", ("test_file", open(test_files[1], "rb"), "image/jpeg")),
    ]
    response = await async_client.post(
        "/frames/",
        headers={"Authorization": f"Bearer {access_token}"},
        files=multiple_files,
    )
    test_object_name = response.json()["user_objects"][1]["object_name"]
    test_bucket_name = datetime.now().strftime("%Y-%m-%d")
    logger.info(
        f"Create test object: {test_object_name} " f"in bucket: {response.json()['user'] + '-' + test_bucket_name}"
    )
    return test_object_name, test_bucket_name
