from typing import Awaitable, Callable

import pytest

from src.infrastructure.db.models import UserModel

import factory

from .base import BaseFactory, create_entity


class UserModelFactory(BaseFactory):
    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n + 1)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("name")
    bio = factory.Faker("sentence")


@pytest.fixture(scope="function")
def patch_user_session(native_db_session):
    UserModelFactory._meta.sqlalchemy_session = native_db_session  # noqa: SLF001 # type: ignore


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
