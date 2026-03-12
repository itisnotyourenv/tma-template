from dataclasses import dataclass, field

from src.presentation.api.base.schemas import BaseResponseDTO


@dataclass
class HealthCheckResponse:
    success: bool = field(default=True)
    message: str = field(default="Service is healthy")


class HealthCheckResponseSchema(BaseResponseDTO[HealthCheckResponse]): ...
