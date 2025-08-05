from http import HTTPStatus

from httpx import AsyncClient

from src.infrastructure.config import Config


class TestAuth:
    url = "auth"

    async def test_auth_failure_with_invalid_init_data(self, test_client: AsyncClient):
        data = {"init_data": "smth"}

        response = await test_client.post(self.url, json=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {
            "detail": "Invalid init data 'smth'",
            "status_code": 400,
        }

    async def test_auth_success_for_new_user(
        self, test_client: AsyncClient, test_config: Config
    ):
        data = {"init_data": test_config.telegram.tg_init_data}

        response = await test_client.post(self.url, json=data)

        assert response.status_code == HTTPStatus.CREATED
        response_data = response.json()
        assert response_data.get("access_token") is not None
