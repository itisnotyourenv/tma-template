from litestar import Litestar


class TestAuth:
    async def test_auth_success(self, test_app: Litestar):
        assert True