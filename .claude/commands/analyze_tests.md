---
description: Audit the test suite for speed, consistency, and reliability, then return issue drafts
argument-hint: [optional-focus]
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
  - Bash(uv run pytest:*)
  - Bash(just test:*)
---

Review the repository's test suite, with emphasis on `tests/`, shared fixtures, helper factories, and any supporting test configuration that explains current behavior.

If the user supplies an argument, treat it as a focus area (for example a subdirectory, file, or concern) and still note any high-severity cross-cutting issues you discover.

## What to evaluate

### 1. Execution speed and bottlenecks
Identify slow or wasteful patterns such as:
- duplicated or expensive fixtures
- unnecessary database, network, filesystem, or external-service I/O
- `sleep()` / timing-based waits / retry loops that create flakiness
- repeated test bodies that should be parameterized
- integration coverage being used where a smaller unit test would prove the same behavior
- setup/teardown work that is much broader than the assertions require

### 2. Consistency and testing style
Look for:
- mixed testing styles or frameworks without a clear reason
- inconsistent naming for tests, fixtures, factories, or helper modules
- weak Arrange/Act/Assert structure
- assertions that are too vague or do not prove the important outcome
- hidden coupling through global state, ordering, shared data, or environment assumptions
- scattered utility code that should be centralized

### 3. Reliability and maintainability
Assess:
- whether tests are deterministic and isolated
- whether failure messages are actionable
- whether edge cases and error paths are covered
- whether helpers/fixtures communicate intent clearly
- whether the suite is easy to extend without copying patterns

### 4. Recommendations
For every meaningful finding, propose a concrete fix. Prefer recommendations that match the existing stack and configuration in this repo.

## Evidence rules
- Cite the exact file paths, test names, fixtures, or helpers involved.
- Do not claim slowness, flakiness, or duplication without evidence.
- If you need to run tests, prefer repo-native commands such as `uv run pytest <path>` or `just test` instead of bare `pytest`.
- Run the narrowest command that proves the point; do not burn time on full-suite runs when a focused command is enough.

## Output
Return all of the following:
1. An executive summary.
2. A findings table with severity, evidence, impact, and recommendation.
3. GitHub issue drafts for each distinct problem area.

Each issue draft must include:
- title
- problem summary
- why it matters
- recommended change
- affected files/tests

Do not create live GitHub issues unless the user explicitly asks. Return drafts only.
