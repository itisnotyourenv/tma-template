from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.infrastructure.config import Config


class TestUserProfile:
    url = "users/profile"

    async def _get_auth_token(self, test_client: AsyncClient, test_config: Config) -> str:
        """Helper method to get a valid JWT token for testing."""
        auth_data = {
            "init_data": test_config.telegram.tg_init_data
        }
        
        response = await test_client.post("auth", json=auth_data)
        assert response.status_code == HTTPStatus.CREATED
        
        response_data = response.json()
        return response_data["access_token"]

    async def _create_authenticated_client(
        self, 
        test_client: AsyncClient, 
        test_config: Config
    ) -> AsyncClient:
        """Helper method to create an authenticated client with JWT token."""
        token = await self._get_auth_token(test_client, test_config)
        test_client.headers.update({"Authorization": f"Bearer {token}"})
        return test_client

    async def test_get_profile_success(
        self,
        test_client: AsyncClient,
        test_config: Config,
    ):
        """Test successful profile retrieval for authenticated user."""
        client = await self._create_authenticated_client(test_client, test_config)

        response = await client.get(self.url)

        assert response.status_code == HTTPStatus.OK
        
        profile_data = response.json()
        # Verify response structure
        assert "id" in profile_data
        assert "first_name" in profile_data
        assert "last_name" in profile_data
        assert "username" in profile_data
        assert "bio" in profile_data
        
        # Verify data types
        assert isinstance(profile_data["id"], int)
        assert isinstance(profile_data["first_name"], str)
        
        # Verify user data from test config
        assert profile_data["first_name"] == "min"
        assert profile_data["username"] == "zurab"

    async def test_get_profile_unauthorized_no_auth_header(
        self,
        test_client: AsyncClient,
    ):
        """Test profile retrieval without authentication."""
        response = await test_client.get(self.url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_profile_unauthorized_invalid_token(
        self,
        test_client: AsyncClient,
    ):
        """Test profile retrieval with invalid authentication token."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = await test_client.get(self.url, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_profile_unauthorized_malformed_auth_header(
        self,
        test_client: AsyncClient,
    ):
        """Test profile retrieval with malformed Authorization header."""
        headers = {"Authorization": "InvalidFormat token"}
        
        response = await test_client.get(self.url, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_profile_response_structure(
        self,
        test_client: AsyncClient,
        test_config: Config,
    ):
        """Test that profile response has correct structure and data types."""
        client = await self._create_authenticated_client(test_client, test_config)

        response = await client.get(self.url)

        assert response.status_code == HTTPStatus.OK
        
        profile_data = response.json()
        
        # Test all required fields exist
        required_fields = ["id", "first_name", "last_name", "username", "bio"]
        for field in required_fields:
            assert field in profile_data, f"Field '{field}' missing from response"
        
        # Test data types
        assert isinstance(profile_data["id"], int)
        assert isinstance(profile_data["first_name"], str)
        
        # Optional fields can be None or strings
        for field in ["last_name", "username", "bio"]:
            assert profile_data[field] is None or isinstance(profile_data[field], str)

    async def test_get_profile_multiple_requests_consistent(
        self,
        test_client: AsyncClient,
        test_config: Config,
    ):
        """Test that multiple profile requests return consistent data."""
        client = await self._create_authenticated_client(test_client, test_config)

        # Make first request
        response1 = await client.get(self.url)
        assert response1.status_code == HTTPStatus.OK
        profile1 = response1.json()

        # Make second request
        response2 = await client.get(self.url)
        assert response2.status_code == HTTPStatus.OK
        profile2 = response2.json()

        # Both responses should be identical
        assert profile1 == profile2

    async def test_get_profile_different_auth_sessions(
        self,
        test_client: AsyncClient,
        test_config: Config,
    ):
        """Test profile retrieval with different authentication sessions."""
        # Create first authenticated client
        client1 = await self._create_authenticated_client(test_client, test_config)
        response1 = await client1.get(self.url)
        assert response1.status_code == HTTPStatus.OK
        profile1 = response1.json()

        # Create second authenticated client (new session)
        test_client.headers.clear()  # Clear previous auth headers
        client2 = await self._create_authenticated_client(test_client, test_config)
        response2 = await client2.get(self.url)
        assert response2.status_code == HTTPStatus.OK
        profile2 = response2.json()

        # Should return same user data since same Telegram init data
        assert profile1["id"] == profile2["id"]
        assert profile1["first_name"] == profile2["first_name"]
        assert profile1["username"] == profile2["username"]

    @pytest.mark.parametrize("malformed_token", [
        "",
        "Bearer",
        "Bearer ",
        "NotBearer validtoken",
        "Bearer invalid.jwt.token",
    ])
    async def test_get_profile_malformed_tokens(
        self,
        test_client: AsyncClient,
        malformed_token: str,
    ):
        """Test profile retrieval with various malformed tokens."""
        headers = {"Authorization": malformed_token}
        
        response = await test_client.get(self.url, headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
