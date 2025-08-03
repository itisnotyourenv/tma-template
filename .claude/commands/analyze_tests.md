# 📊 Prompt: Test Directory Audit with GitHub Issue Generation

Please analyze the contents of the `tests/` directory in this project. Perform a thorough audit and complete the following tasks:

---

## 🚀 1. Performance Bottlenecks

- Identify any **slowdowns in test execution**, including:
  - heavy or duplicated fixtures
  - real interactions with database, network, or external services instead of mocks
  - unnecessary `sleep()` or artificial delays
  - unparameterized tests running the same logic repeatedly
  - overly broad test scopes (e.g. using integration tests where unit tests suffice)
- Recommend **optimizations** (e.g., `pytest.mark.parametrize`, `pytest-xdist`, mocking with `unittest.mock`, using factory libraries like `factory_boy`)
- Suggest areas where **parallelization** can be applied

---

## 🧬 2. Style Consistency & Testing Patterns

- Identify what **testing styles** are used (e.g., unit, integration, e2e, property-based)
- Detect **inconsistencies in test structure or format**, such as:
  - Mixing different testing frameworks (`pytest`, `unittest`, etc.)
  - Varying naming conventions for test functions or fixtures
  - Inconsistent use of `Arrange-Act-Assert` pattern
  - Non-uniform use of fixtures, mocks, or `assert` statements
  - Scattered test utility code (e.g., missing or messy `conftest.py`)
- Spot common **anti-patterns**, like:
  - tests with side effects
  - tests dependent on execution order
  - test cases without assertions
  - tests that cover too much logic at once

---

## 🛠 3. Improvements & Best Practices

- Propose **specific improvements** for:
  - speed
  - readability
  - reliability
  - test coverage
- Highlight where **testing best practices** can be applied:
  - `pytest.raises`, `autouse=True` fixtures
  - factory functions instead of raw object creation
  - centralized config with `pytest.ini` or `tox.ini`

---

## 📌 4. Create a GitHub Issue for Each Finding

For **each discovered issue or opportunity for improvement**, do the following:

- Create a **separate GitHub issue** with:
  - A clear and concise **title**
  - A description of the **problem or inconsistency**
  - Explanation of **why it's a concern**
  - A specific and actionable **recommendation**
  - Optional: **Links or references to lines/files**, if available
- If the same problem appears in multiple places, summarize it in **a single issue**, listing all occurrences

---

Once the analysis is complete, return:

- A structured **summary report**
- A list of **GitHub issue drafts** (title + content) for easy copy-paste
