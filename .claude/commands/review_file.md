---
description: Review a single file and return actionable findings with evidence
argument-hint: <file-path>
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
---

Review the file provided in the argument.
Understand what it does before judging how it does it.

## Review goals

### 1. Purpose and system role
Explain:
- the file's responsibility
- the main symbols it defines
- how it connects to nearby modules, callers, or framework boundaries

### 2. Correctness and contracts
Look for:
- logic bugs
- hidden assumptions about inputs, environment, or ordering
- misleading return values or error handling
- contracts that callers could misunderstand
- edge cases that appear unhandled

### 3. Design and maintainability
Assess:
- separation of concerns
- clarity of naming and structure
- duplication and opportunities to reuse existing patterns
- whether abstractions cover their domain honestly
- whether the next maintainer will understand the intended invariants

### 4. Testing and operational risk
Call out:
- missing or weak tests
- fragile branches or failure modes
- security or performance concerns when relevant
- places where comments or naming should explain non-obvious intent

## Output format
Return a structured review with:
1. File purpose and system context.
2. Must-fix findings.
3. Suggestions and refactors.
4. Missing tests or validation gaps.
5. Open questions.
6. Optional GitHub issue drafts for distinct follow-up items.

For each finding, cite concrete evidence such as file paths, symbol names, and the behavior at risk.
Do not create GitHub issues unless the user explicitly asks; return drafts only.
