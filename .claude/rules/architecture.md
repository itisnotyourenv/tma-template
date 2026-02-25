# Architecture

Four-layer Clean Architecture with inward dependency rule:

Presentation → Infrastructure → Application → Domain

## Layers

### Domain (`src/domain/`)
- Entities as dataclasses (`src/domain/user/entity.py`)
- Value Objects with validation, inherit from `BaseValueObject[T]` (`src/domain/common/vo/base.py`)
- Repository protocols — abstract interfaces using `Protocol` (`src/domain/user/repository.py`)
- No dependencies on other layers

### Application (`src/application/`)
- Interactors (use cases) inherit from `Interactor[InputDTO, OutputDTO]`, implement `__call__`
- DTOs are dataclasses, live in application layer (not domain)
- `UserService` handles upsert logic to avoid duplication across interactors
- `TransactionManager` protocol for commit control

### Infrastructure (`src/infrastructure/`)
- `db/models/` — SQLAlchemy ORM models with custom TypeDecorator for Value Objects
- `db/mappers/` — Bidirectional domain ↔ ORM conversion (`UserMapper.to_domain()` / `.to_model()`)
- `db/repos/` — Repository implementations (inherit protocol + `BaseSQLAlchemyRepo`)
- `db/migrations/` — Alembic (script location: `src/infrastructure/db/migrations`)
- `di/` — Dishka providers: `DBProvider`, `AuthProvider`, `I18nProvider`; Scopes: `APP` for singletons, `REQUEST` for per-request
- `config.py` — Pydantic config loaded from YAML

### Presentation (`src/presentation/`)
- `api/` — Litestar REST API (controllers, auth middleware, health check)
- `bot/` — Aiogram Telegram bot (routers, middleware for user & locale)

## Dependency Direction

Domain knows nothing about other layers. Application depends only on domain.
Infrastructure implements domain protocols. Presentation depends on all layers
but only accesses domain/application through DI.
