import pytest


@pytest.mark.anyio
class TestDeleteRoute:
    async def test_delete_all_images(self, async_client, create_test_objects):
        bucket_name = create_test_objects[1]
        response = await async_client.get(f"/frames/{bucket_name}")
        assert response.status_code == 200

    async def test_delete_one_image(self, async_client, create_test_objects):
        bucket_name = create_test_objects[1]
        response = await async_client.get(
            f"/frames/{bucket_name}",
            params={"object_name": create_test_objects[0]},
        )
        assert response.status_code == 200

    async def test_delete_images_from_nonexistent_bucket(self, async_client):
        response = await async_client.get("/frames/2022-06-30")
        assert response.status_code == 404
