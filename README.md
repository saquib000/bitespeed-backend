# Identity Reconciliation Service

A backend service that reconciles customer identities across multiple purchases based on shared email addresses or phone numbers.

This project implements the Bitespeed Backend Task – Identity Reconciliation.

---

## 🌐 Live API

**Base URL:**  
https://bitespeed-backend-gduh.onrender.com/

**Endpoint:**  
POST /identify

Example:

```

POST https://bitespeed-backend-gduh.onrender.com/identify

````

---

## 📌 Problem Overview

Customers may use different email addresses and phone numbers across purchases.

The system must:

- Identify whether an incoming request belongs to an existing customer
- Link contacts that share email OR phone number
- Maintain exactly one **primary contact** per identity group
- Convert older or newer primaries into secondaries when groups merge
- Return a consolidated identity response

---

## 🧠 Core Idea

This problem is modeled as a **dynamic connected components problem**:

- Each `Contact` is a node
- Contacts sharing email or phone belong to the same component
- Each component has:
  - Exactly one **primary contact** (oldest record)
  - Zero or more **secondary contacts**

On every `/identify` request:

1. Find matching contacts
2. Expand the full connected identity group
3. Determine the canonical primary (oldest contact)
4. Merge groups if multiple primaries exist
5. Create a secondary contact if the email/phone combination is new
6. Return a deterministic consolidated response

---

## 🏗 Architecture

The project follows a layered architecture:

```
app/
 ├── main.py
 ├── database.py
 ├── models/
 ├── schemas/
 ├── repositories/
 ├── services/
 └── routers/
```

### Layers

- **Router** → Handles HTTP request/response
- **Service Layer** → Identity resolution logic
- **Repository Layer** → Database operations
- **Models** → SQLAlchemy ORM definitions
- **Schemas** → Pydantic request/response models

---

## 🗄 Database Schema

Table: `contacts`

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| email | String | Optional email |
| phoneNumber | String | Optional phone |
| linkedId | Integer | References primary contact |
| linkPrecedence | String | "primary" or "secondary" |
| createdAt | DateTime | Creation timestamp |
| updatedAt | DateTime | Update timestamp |
| deletedAt | DateTime | Soft delete field |

---

## 🔁 Identity Rules Enforced

✔ Exactly one primary per identity group  
✔ All secondaries directly reference the primary  
✔ No secondary → secondary chains  
✔ Oldest contact always becomes canonical primary  
✔ New combinations create secondary contacts  
✔ Fully transaction-safe operations  

---

## 📥 Request Format

```json
{
  "email": "string (optional)",
  "phoneNumber": "string (optional)"
}
```

At least one field must be provided.

---

## 📤 Response Format

```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": ["primary@email.com", "other@email.com"],
    "phoneNumbers": ["123456", "789101"],
    "secondaryContactIds": [2, 3]
  }
}
```

Response guarantees:

- Primary contact appears first in emails and phoneNumbers
- No duplicate values
- Deterministic ordering

---

## 🧪 Automated Testing

Minimal pytest suite included to validate:

- New identity creation
- Secondary creation
- Primary merging
- No secondary chaining
- Single primary per identity group

Run tests:

```bash
pytest
```

---

## 🚀 Running Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Start server

```bash
uvicorn app.main:app --reload
```

### 3️⃣ Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## 🛠 Tech Stack

- FastAPI
- SQLAlchemy 2.0
- SQLite
- Pytest
- Uvicorn

---

## 🔒 Transaction Safety

All identity resolution logic runs inside a database transaction to ensure:

- Atomic merges
- No inconsistent states
- No multiple primaries in a group

---

## 🎯 Design Considerations

- Modeled as connected component resolution
- Flat hierarchy enforced
- Deterministic response ordering
- Repository pattern for clean separation of concerns
- Fully deployable as a stateless web service

---

## 📌 Deployment

Hosted on Render.

Start command:

```
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

## 📎 Author

Mohammad Saquib  
Backend Developer | Data Science & Applications, IIT Madras
