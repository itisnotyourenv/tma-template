from httpx import AsyncClient


class TestHealth:
    url = 'health'

    async def test_get_health_success(self, test_client: AsyncClient):
        response = await test_client.get(
            self.url,
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Service is healthy",
            "success": True,
        }
