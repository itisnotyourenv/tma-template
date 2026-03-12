from collections.abc import Collection

from litestar.dto import DataclassDTO, DTOConfig
from litestar.types.protocols import DataclassProtocol
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

type DataclassDTOData = DataclassProtocol | Collection[DataclassProtocol]


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class BaseRequestDTO[T: DataclassDTOData](DataclassDTO[T]):
    config = DTOConfig(
        rename_strategy="camel",
    )


class BaseResponseDTO[T: DataclassDTOData](DataclassDTO[T]):
    config = DTOConfig(
        rename_strategy="camel",
        max_nested_depth=3,
    )
