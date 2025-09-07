---
allowed-tools: 
  - Bash(git status:*)
  - Bash(git diff --cached:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git log:*)

description: Create a git commit according to our git styleguide (assumes code was written by an agent)
---

# Agent Guide: Prepare and Create a Commit

## 0) General Rules
- Use **Conventional Commits + emoji** format:  
  `<emoji> <type>(<scope>): <short summary>`  
  Example: `✨ feat(auth): add refresh token rotation`
- **Short summary ≤ 72 chars**, no period at the end.
- The body should briefly explain **why** and **what** changed; add `BREAKING CHANGE: ...` if applicable.
- Commit **only relevant** changes (exclude IDE artifacts, `.env`, caches, etc.).

## 1) If the current branch is `main` (or `master`)
1. Determine the appropriate `type` and `scope` (see table below).
2. Create a new branch using the template:
   - Feature: `feat/<scope>-<short-slug>`
   - Fix: `fix/<scope>-<short-slug>`
   - Other: `<type>/<scope>-<short-slug>`


## 2) Run quality gates **before** committing
1. Ruff (format + lint):
   ```bash
   # If Ruff formatter is enabled:
   ruff format .
   # Lint and auto-fix simple issues:
   ruff check . --fix
   ```
2. Pytest:
   ```bash
   # Prefer parallel & quick run if available
   pytest -n auto -q --maxfail=1
   ```
3. If **Ruff or Pytest fail**, **DO NOT** commit. Fix issues and rerun.

## 3) Compose the commit message
Decide on **type** and **scope** (see table). Craft a concise summary (**what**), and write a short body explaining **why/how**.  
If there are API changes or incompatibilities, add:

```
BREAKING CHANGE: <brief description and migration notes>
```

### Commit message template
```
<emoji> <type>(<scope>): <short summary>

<why/what/how — 1–3 short paragraphs; bullet points if helpful>
- <key change 1>
- <key change 2>

Refs: <issue/PR links or IDs>
```

### Create the commit
```bash
git commit -m "<emoji> <type>(<scope>): <short summary>" -m "<body>"
```

## 4) Types and emojis

| Type     | Emoji | Use for                                | Example headline                                         |
|----------|-------|----------------------------------------|----------------------------------------------------------|
| feat     | ✨    | New feature / behavior change          | `✨ feat(parser): support CSV delimiter option`          |
| fix      | 🐞    | Bug fix                                | `🐞 fix(auth): handle expired refresh token`             |
| docs     | 📝    | Docs, README, comments                 | `📝 docs(readme): add setup section`                     |
| refactor | ♻️    | Code restructuring w/o behavior change | `♻️ refactor(api): extract service layer`                |
| perf     | ⚡    | Performance improvements               | `⚡ perf(query): add composite index`                    |
| test     | ✅    | Tests, fixtures                        | `✅ test(user): add repository edge cases`               |
| chore    | 🧹    | Maintenance, configs, no logic changes | `🧹 chore(repo): update pre-commit hooks`                |
| build    | 🛠️    | Build system, dependencies             | `🛠️ build: bump sqlalchemy to 2.0.35`                   |
| ci       | 🤖    | CI/CD pipelines                        | `🤖 ci: add pytest cache artifact`                       |
| style    | 🎨    | Formatting / style (no logic)          | `🎨 style: reorder imports with ruff`                    |

> **scope** — a concrete module/layer/service, e.g., `auth`, `user`, `api`, `db`, `bot`, `course`, `infra`, `ci`, `docs`, etc.

## 5) Good summary rules
- Imperative mood verbs: *add*, *fix*, *update*, *remove*, *refactor*, *adjust*.
- No trailing period; keep to ≤ 72 characters.
- Avoid vague phrases like “minor fixes”, “small changes”.

## 6) Commit body (when needed)
- Explain **why** the change is needed; **what** exactly changed; **side effects**.
- For bug fixes — include reproduction conditions.
- For perf/refactor — mention motivation/metrics/scope of impact.
- Add `Refs: #123` or a link to the ticket when applicable.

## 7) Post-commit (optional)
- If this is the first commit in a feature/fix branch, make sure to link the task/issue in the PR description when you open it.
- Push the branch:
  ```bash
  git push --set-upstream origin "$(git branch --show-current)"
  ```

---

### Quick checklist for the agent
1. **Branch check**: if on `main/master` → create a new branch (`<type>/<scope>-<short-slug>`).
2. **Inspect changes**: `git status`, commit only staged files.
3. **Quality gates**: `ruff format .` → `ruff check . --fix` → `pytest -n auto -q --maxfail=1`. If failing → fix, then rerun.
4. **Message**: `<emoji> <type>(<scope>): <short summary>` + body and `BREAKING CHANGE` if needed.
5. **Commit**: `git commit -m ... -m ...`.
6. **Push** (if you plan a PR): `git push -u origin <branch>`.
