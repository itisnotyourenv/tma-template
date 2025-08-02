from typing import TypeVar

from factory.alchemy import SQLAlchemyModelFactory

from src.infrastructure.db.models.base import BaseORMModel


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        model = None

BaseSubclassT = TypeVar("BaseSubclassT", bound=type[BaseORMModel])


async def create_entity(entity_factory: type[BaseFactory], use_cache: bool = False, **kwargs) -> BaseSubclassT:
    # Create new entity
    entity = entity_factory.create(**kwargs)
    await entity_factory._meta.sqlalchemy_session.commit()

    return entity