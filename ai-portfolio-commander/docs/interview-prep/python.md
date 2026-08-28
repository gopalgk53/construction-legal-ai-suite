# Python Interview Questions

## Q1. What problem does a virtual environment solve?

### Junior Answer
Virtual environments help install packages separately.

### Mid-Level Answer
Virtual environments isolate project dependencies and prevent package conflicts between projects.

### Senior Answer
Virtual environments provide dependency isolation, reproducibility, and deployment consistency. They allow different projects to use different package versions without affecting one another.

### Real-World Example

Project A:

FastAPI 0.115

Project B:

FastAPI 0.102

Virtual environments prevent one project from breaking the other.

### Follow-up Questions

- How do you create a virtual environment?
- How does activation work?
- What is requirements.txt?
- What is pyproject.toml?

---

## Q2. What would happen if all projects shared the same packages?

### Junior Answer
Projects could stop working.

### Mid-Level Answer
Package version conflicts may occur.

### Senior Answer
Shared dependencies create coupling between projects. Upgrading a package for one application can introduce failures in unrelated applications.

---

## Q3. Why is reproducibility important?

### Junior Answer
It helps others run the code.

### Mid-Level Answer
It ensures everyone gets the same result.

### Senior Answer
Reproducibility ensures consistent behavior across development, testing, and production environments. It reduces deployment risk and improves reliability.

---

## Q4. What is a class?

### Junior Answer
A class creates objects.

### Mid-Level Answer
A class is a template for creating objects.

### Senior Answer
A class is a blueprint that encapsulates state and behavior into reusable components.
