# System Design Questions

## Q1. Design a Document Intelligence Platform

### Requirements

Functional:

- Upload PDFs
- OCR extraction
- Search documents
- Extract fields

Non-Functional:

- Scalability
- Reliability
- Security

### Architecture

User

↓

FastAPI

↓

OCR Service

↓

PostgreSQL

↓

Vector Database

↓

AI Services

---

## Q2. What happens at 10x traffic?

### Senior Answer

Identify bottlenecks:

- Database
- OCR Pipeline
- AI APIs

Possible solutions:

- Caching
- Queueing
- Horizontal scaling
- Load balancing
