from litestar.dto import DTOConfig
from litestar.dto.dataclass_dto import DataclassDTO, T


class BaseResponseDTO(DataclassDTO[T]):
    config = DTOConfig(
        rename_strategy="camel",
        max_nested_depth=3,
    )
