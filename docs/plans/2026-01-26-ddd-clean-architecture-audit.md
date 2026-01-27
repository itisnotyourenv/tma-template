# Архитектурный аудит: DDD и Clean Architecture

**Дата:** 2026-01-26
**Тип:** Строгий архитектурный аудит
**Фокус:** Слои и Dependency Rule

---

## Обзор

Проведён аудит проекта TMA Template на соответствие принципам DDD и Clean Architecture. Проверены направления зависимостей, изоляция слоёв, соблюдение Dependency Rule.

### Текущая структура слоёв

```
src/
├── domain/          # Entities, Value Objects, Repository Protocols
├── application/     # Interactors (Use Cases), Interfaces, DTOs
├── infrastructure/  # DB, Auth implementations, DI Providers
└── presentation/    # API (Litestar), Bot (Aiogram)
```

### Dependency Rule

Зависимости направлены внутрь (к Domain):

```
Presentation (внешний)
    ↓
Infrastructure
    ↓
Application
    ↓
Domain (внутренний)
```

---

## Найденные нарушения

### Приоритет 1 — Критические

#### 1. DTO в Domain Layer

**Файл:** `src/domain/user/repository.py:8-23`

**Проблема:** `CreateUserDTO` и `UpdateUserDTO` определены в Domain Layer и содержат примитивы (`int`, `str`) вместо Value Objects.

```python
class CreateUserDTO(TypedDict):
    id: int              # примитив, не UserId
    username: str | None # примитив, не Username
    first_name: str      # примитив, не FirstName
```

**Почему критично:**
- Domain Layer не должен знать о DTO — это транспортный механизм Application Layer
- Repository Protocol в домене должен работать с Domain Entity или Value Objects

**Решение:** Переместить DTO в Application Layer. Repository должен принимать `User` entity.

---

#### 4. Repository принимает примитивы вместо доменных типов

**Файл:** `src/domain/user/repository.py:37-44`

**Проблема:** Repository принимает "сырые" примитивы, обходя валидацию Value Objects.

```python
async def create_user(self, user: CreateUserDTO) -> User:  # CreateUserDTO содержит примитивы
```

**Почему критично:**
- Можно передать невалидный `id: -1`
- Можно передать `first_name: ""` (пустую строку)
- Value Objects существуют, но не используются на границе репозитория

**Решение:**
```python
async def create_user(self, user: User) -> User:
```

---

#### 7. Дублирование логики upsert user

**Файлы:**
- `src/application/user/create.py:42-66`
- `src/application/auth/tg.py:34-57`

**Проблема:** Идентичная логика "get user → create or update" в двух Interactors.

```python
# Оба Interactor содержат:
user = await self.user_repository.get_user(user_id)
if user is None:
    user = await self.user_repository.create_user(...)
else:
    user = await self.user_repository.update_user(...)
await self.transaction_manager.commit()
```

**Почему критично:**
- При изменении логики нужно менять оба места
- Риск рассинхронизации (уже есть: `AuthTgInteractor` не возвращает `user` после update)

**Решение:** Выделить Domain Service `UserService.upsert(data) -> User` или использовать композицию Interactors.

---

### Приоритет 2 — Важные

#### 8. Нет Unit of Work паттерна

**Файлы:**
- `src/application/common/transaction.py`
- Все Interactors

**Проблема:** `TransactionManager` отделён от репозиториев. Каждый Interactor должен вручную вызывать `commit()`.

```python
# В каждом Interactor
user = await self.user_repository.create_user(...)
await self.transaction_manager.commit()  # легко забыть
```

**Риск:** Забытый `commit()` = потеря данных без ошибки.

**Решение — Unit of Work:**
```python
class UnitOfWork(Protocol):
    user_repository: UserRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, *args) -> None: ...  # auto-commit
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

---

#### 3. Presentation создаёт Infrastructure напрямую

**Файл:** `src/presentation/api/app.py:30`

```python
auth_service = AuthServiceImpl(config)  # прямое создание
```

**Проблема:** Presentation Layer создаёт конкретную реализацию из Infrastructure вместо получения через DI.

**Решение:** `AuthService` должен инжектиться через Dishka контейнер.

---

#### 6. NotImplementedError вместо доменного исключения

**Файл:** `src/application/user/get_me.py:35-36`

```python
if not user:
    raise NotImplementedError  # системное исключение
```

**Проблема:** Неинформативное системное исключение. Presentation Layer не может корректно обработать.

**Решение:**
```python
# src/application/user/exceptions.py
class UserNotFoundError(ApplicationError):
    def __init__(self, user_id: UserId):
        super().__init__(f"User {user_id} not found")
```

---

#### 10. Непоследовательная передача Config

**Файл:** `src/presentation/api/app.py:64-68`

```python
container = make_async_container(
    DBProvider(config.postgres),  # через конструктор
    ...
    context={Config: config},     # и через context
)
```

**Проблема:** Два способа передачи конфига — непоследовательно.

**Решение:** Использовать только Dishka context.

---

### Приоритет 3 — Улучшения

#### 5. Маппинг внутри ORM Model

**Файл:** `src/infrastructure/db/models/user.py:33-56`

**Проблема:** `to_domain()` и `from_domain()` внутри ORM Model нарушает Single Responsibility.

**Решение:** Выделить отдельный `UserMapper` класс.

---

#### 9. Лишняя зависимость AuthService

**Файл:** `src/application/user/create.py:36-40`

```python
def __init__(
    self,
    user_repository: UserRepository,
    transaction_manager: TransactionManager,
    auth_service: AuthService,  # не используется
) -> None:
```

**Проблема:** `CreateUserInteractor` инжектит `AuthService`, но не использует его.

**Решение:** Убрать неиспользуемую зависимость.

---

## План действий

### Этап 1 — Быстрые победы (1-2 дня)

- [x] Убрать неиспользуемую зависимость `AuthService` из `CreateUserInteractor`
- [x] Заменить `NotImplementedError` на `UserNotFoundError`
- [x] Перенести создание `AuthServiceImpl` в DI контейнер
- [x] Унифицировать передачу `Config` через Dishka context

### Этап 2 — Рефакторинг Domain/Application (3-5 дней)

- [x] Вынести логику upsert user в Domain Service или единый Interactor
- [x] Переместить `CreateUserDTO`/`UpdateUserDTO` в Application Layer
- [x] Изменить сигнатуру Repository: принимать `User` entity вместо DTO
- [x] Создать доменные исключения (`UserNotFoundError`, `InvalidUserDataError`)

### Этап 3 — Архитектурные улучшения (5-7 дней)

- [ ] Внедрить Unit of Work паттерн
- [x] Выделить отдельные Mapper классы
- [ ] Ревью и рефакторинг остальных слоёв по тем же принципам

---

## Сводная таблица

| # | Проблема | Приоритет | Влияние | Риск | Сложность |
|---|----------|-----------|---------|------|-----------|
| 1 | DTO в Domain Layer | P1 | Высокое | Средний | Средняя |
| 4 | Repository принимает примитивы | P1 | Высокое | Высокий | Средняя |
| 7 | Дублирование логики upsert | P1 | Высокое | Высокий | Низкая |
| 8 | Нет Unit of Work | P2 | Среднее | Высокий | Средняя |
| 3 | Presentation создаёт Infrastructure | P2 | Среднее | Низкий | Низкая |
| 6 | NotImplementedError | P2 | Среднее | Средний | Низкая |
| 10 | Непоследовательный Config | P2 | Низкое | Низкий | Низкая |
| 5 | Маппинг внутри ORM Model | P3 | Низкое | Низкий | Средняя |
| 9 | Лишняя зависимость AuthService | P3 | Низкое | Низкий | Низкая |
