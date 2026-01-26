from collections.abc import Awaitable, Callable
from datetime import UTC, datetime

import factory
import pytest

from src.infrastructure.db.models import UserModel

from .base import BaseFactory, create_entity


class UserModelFactory(BaseFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 1)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("name")
    bio = factory.Faker("sentence")
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(UTC))
    last_login_at = factory.LazyFunction(lambda: datetime.now(UTC))


@pytest.fixture(scope="function")
def patch_user_session(native_db_session):
    UserModelFactory._meta.sqlalchemy_session = native_db_session  # type: ignore


@pytest.fixture(scope="function")
async def create_user(patch_user_session) -> Callable[..., Awaitable[UserModel]]:
    async def _create(**kwargs):
        return await create_entity(UserModelFactory, **kwargs)

    return _create


@pytest.fixture(scope="function")
async def test_user(
    create_user: Callable[..., Awaitable[UserModel]],
) -> UserModel:
    return await create_user()
