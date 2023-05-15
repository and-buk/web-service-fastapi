from datetime import datetime

import pytest
from pydantic import UUID4, BaseModel


class Response(BaseModel):
    user_name: str
    id: UUID4
    created_at: datetime


@pytest.mark.anyio
class TestAddUser:
    async def test_add_new_user(self, async_client):
        payload = {
            "user_name": "dan",
            "first_name": "dan",
            "second_name": "dan",
            "email": "dan@example.com",
            "password": "dan",
        }
        response = await async_client.post("users/", json=payload)
        response_data = response.json()
        assert response.status_code == 201
        assert Response.parse_obj(response.json())
        assert response_data["user_name"] == "dan"

    async def test_add_new_user_without_req_atrr(self, async_client):
        payload = {
            "first_name": "dan",
            "second_name": "dan",
            "email": "dan@example.com",
            "password": "dan",
        }
        response = await async_client.post("users/", json=payload)
        assert response.status_code == 422
