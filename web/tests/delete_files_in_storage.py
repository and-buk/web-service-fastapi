import pytest


@pytest.mark.anyio
class TestDeleteRoute:
    async def test_delete_all_images(self, async_client, create_test_objects, user_auth):
        bucket_name = create_test_objects[1]
        access_token = user_auth["access_token"]
        response = await async_client.delete(
            f"/frames/{bucket_name}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    async def test_delete_one_image(self, async_client, create_test_objects, user_auth):
        bucket_name = create_test_objects[1]
        access_token = user_auth["access_token"]
        response = await async_client.delete(
            f"/frames/{bucket_name}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"object_name": create_test_objects[0]},
        )
        assert response.status_code == 200

    async def test_delete_images_from_nonexistent_bucket(self, async_client, user_auth):
        access_token = user_auth["access_token"]
        response = await async_client.delete(
            "/frames/2022-06-30",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404
