**🛠️ Prompt: Review File – `$FILE_NAME`**

You are tasked with reviewing the file: **`$FILE_NAME`**

Follow the steps below:

---

### 1. 🔍 **Understand the File’s Purpose**
- Analyze the code to understand what it does and why it exists.
- Determine how it fits into the larger system or domain.

✅ **Goal:**  
After forming a clear understanding, **create a GitHub issue** with:
- A **summary of the file's purpose**
- A brief explanation of how it connects to other parts of the system
- Any **open questions**, uncertainties, or architectural concerns

---

### 2. 🧹 **Analyze Code Quality**
Review the Python code for:
- Clarity, simplicity, and readability
- Adherence to [PEP 8](https://www.python.org/dev/peps/pep-0008/) and Pythonic practices
- Proper naming and modular structure
- Safe error handling and input validation
- Use of idioms and patterns consistent with the codebase

---

### 3. 🧠 **Evaluate Design & Maintainability**
Assess:
- Code organization and separation of concerns
- Application of SOLID, DRY, and KISS principles
- Scalability, extensibility, and testability
- Reusability of components and avoidance of duplication

---

### 4. 🧪 **Suggest Improvements**
Identify all potential improvements such as:
- Refactoring opportunities
- Risk areas or potential bugs
- Performance optimizations
- Missing or weak test coverage

---

### 5. 📝 **Create a GitHub Issue with Sub-Issues**
Once the review is complete:

- Open **one primary GitHub issue** titled:  
  `"Code Review – $FILE_NAME"`
  
- In the issue body, include:
  - A high-level summary of your analysis
  - A task list using GitHub markdown to represent **each finding or improvement**:
  
```md
## 🔧 Review Summary: `$FILE_NAME`

- File Purpose: _[Short description]_
- Reviewer: _[Your Name or AI]_
- Review Date: _[YYYY-MM-DD]_

### ✅ Issues & Recommendations

- [ ] Clarify unclear function `X` – purpose is ambiguous  
- [ ] Rename variable `temp` to be more descriptive  
- [ ] Remove unused import `abc`  
- [ ] Add test case for edge condition in `handle_event()`  
- [ ] Refactor nested `if` in `process_data()` for readability  
```

This structure enables your team to track review findings as **subtasks**, delegate work, and mark resolutions individually.
