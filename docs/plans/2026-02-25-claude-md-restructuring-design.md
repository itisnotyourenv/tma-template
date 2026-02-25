# CLAUDE.md Restructuring Design

**Date:** 2026-02-25
**Goal:** Restructure CLAUDE.md for better effectiveness using progressive disclosure and modular rules.

## Problem

Current CLAUDE.md works but can be improved:
- No critical "Do Not" rules for architectural boundaries
- No git conventions documented
- Architecture, patterns, and testing details always loaded even when not needed
- Missing i18n stub generation workflow

## Solution

Restructure into compact root file + modular `.claude/rules/` files.

## Files

### 1. `CLAUDE.md` (~65 lines)

Compact root file with:
- Project overview (1 line)
- Commands (unchanged)
- Architecture (1 line + reference to rules)
- **Critical Rules** (NEW) — IMPORTANT-marked, always loaded:
  - Business logic MUST live in Interactors only
  - NEVER use repositories directly outside Interactors
  - NEVER pass ORM models to application/domain layers
  - NEVER import from infrastructure in domain/application
- **Git Conventions** (NEW) — emoji conventional commits format
- Configuration (minimal)
- Ruff (minimal)

### 2. `.claude/rules/architecture.md`

Detailed 4-layer description:
- Domain: entities, VOs, repository protocols
- Application: interactors, DTOs, services, transaction manager
- Infrastructure: ORM models, mappers, repos, migrations, DI, config
- Presentation: API (Litestar), Bot (aiogram)
- Dependency direction explanation

### 3. `.claude/rules/patterns.md`

How to create new entities following project patterns:
- Value Objects: inheritance chain, SQLAlchemy TypeDecorator, step-by-step
- Interactor pattern: base class, __call__, DI registration
- Mappers: to_domain/to_model, location
- DI with Dishka: scopes, providers, from_context
- i18n: Fluent format, snake_case keys, stub generation workflow

### 4. `.claude/rules/testing.md`

Testing setup and patterns:
- Config and DB setup
- Running tests (full suite, single file)
- Pytest configuration (async, parallel, coverage)
- Test structure (unit/integration/factories)
- Patterns (class-based, fixtures, AsyncMock, parametrize)
- Factory-boy usage and key integration fixtures

## Principle

CLAUDE.md contains what's needed **always**. Rules load **on demand** when Claude works with relevant files.
