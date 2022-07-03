import logging
import os

import pytest
from httpx import AsyncClient
from .application.main import app, database

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def db():
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
def test_image_png():
    file = os.path.join(ROOT_DIR, "test_data", "test_img_400.png")
    return file


@pytest.fixture()
def test_images_jpeg():
    file_1 = os.path.join(ROOT_DIR, "test_data", "test_img_200.jpeg")
    file_2 = os.path.join(ROOT_DIR, "test_data", "test_img_200_2.jpeg")
    return file_1, file_2


@pytest.fixture()
async def create_test_objects(test_images_jpeg, async_client):
    test_files = test_images_jpeg
    multiple_files = [
        ("files", ("test_file", open(test_files[0], "rb"), "image/jpeg")),
        ("files", ("test_file", open(test_files[1], "rb"), "image/jpeg")),
    ]
    response = await async_client.post("/frames/", files=multiple_files)
    test_object_name = response.json()["objects"][1]["object_name"]
    test_bucket_name = response.json()["objects"][1]["created_at"][:10]
    logger.info(
        f"Create test object: {test_object_name} in bucket: {test_bucket_name}"
    )
    return test_object_name, test_bucket_name
