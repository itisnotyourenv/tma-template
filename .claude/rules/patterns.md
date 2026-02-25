# Key Patterns

## Value Objects

All domain fields use VOs with built-in validation.

- Inherit from `BaseValueObject[T]` (`src/domain/common/vo/base.py`)
- String VOs inherit `NonEmptyString`, set `min_length` / `max_length`
- Integer VOs inherit `PositiveInteger`
- Custom SQLAlchemy `TypeDecorator` in `src/infrastructure/db/models/types/` maps VOs to DB columns

Creating a new VO:
1. Define class in `src/domain/<entity>/vo.py` inheriting from base VO
2. Create `TypeDecorator` in `src/infrastructure/db/models/types/<entity>.py`
3. Use the type in ORM model's `mapped_column()`

## Interactor Pattern

Each use case is a callable async class.

- Inherit `Interactor[InputDTO, OutputDTO]` (`src/application/common/interactor.py`)
- Implement `async def __call__(self, data: InputDTO) -> OutputDTO`
- Inject dependencies via `__init__` (repository, transaction_manager, services)
- Always call `transaction_manager.commit()` after writes
- Register in Dishka provider: `src/infrastructure/di/interactors/`

## Mappers

Bidirectional domain entity ↔ ORM model conversion.

- Static methods: `to_domain(model) -> Entity`, `to_model(entity) -> Model`
- Located in `src/infrastructure/db/mappers/`
- Repositories MUST use mappers — never return ORM models

## DI with Dishka

- Providers in `src/infrastructure/di/`
- `Scope.APP` for singletons (engine, session_maker)
- `Scope.REQUEST` for per-request (session, repos, interactors)
- `from_context()` for config injection
- Integrated into both aiogram and Litestar

## i18n

- Fluent format (`.ftl` files) in `locales/{en,ru}/`
- Keys use `snake_case` (not kebab-case)
- `FluentTranslatorHub` with English fallback
- Type stubs: `src/infrastructure/i18n/types.py` — auto-generated, do NOT edit manually
- After adding/changing `.ftl` keys, regenerate stubs: `just generate-i18n`
  (runs `scripts/generate_i18n_stubs.py`, parses `locales/en/*.ftl` as reference)
- Stubs provide IDE autocomplete for `TranslatorRunner` methods with typed parameters
- Always add keys to BOTH `locales/en/` and `locales/ru/`
