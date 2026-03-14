from http import HTTPStatus

from httpx import AsyncClient


class TestOpenAPI:
    url = "schema/openapi.json"

    async def _get_schema(self, test_client: AsyncClient) -> dict:
        response = await test_client.get(self.url)

        assert response.status_code == HTTPStatus.OK
        return response.json()

    async def test_schema_endpoint_is_public_and_includes_bearer_security_scheme(
        self, test_client: AsyncClient
    ) -> None:
        schema = await self._get_schema(test_client)

        assert schema["security"] == [{"BearerToken": []}]
        assert schema["components"]["securitySchemes"]["BearerToken"] == {
            "type": "http",
            "description": "JWT api-key authentication and authorization.",
            "name": "Authorization",
            "scheme": "Bearer",
            "bearerFormat": "JWT",
        }

    async def test_public_routes_override_global_auth_requirement(
        self, test_client: AsyncClient
    ) -> None:
        schema = await self._get_schema(test_client)

        assert schema["paths"]["/auth"]["post"]["security"] == [{}]
        assert schema["paths"]["/health"]["get"]["security"] == [{}]

    async def test_profile_route_inherits_global_bearer_auth(
        self, test_client: AsyncClient
    ) -> None:
        schema = await self._get_schema(test_client)

        assert "security" not in schema["paths"]["/users/profile"]["get"]
        assert schema["security"] == [{"BearerToken": []}]
