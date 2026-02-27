# 🚀 Perfect 🔥 good repo name.

Your repository name is:

real-time-notification-prioritizer

Now here’s what you should update properly 👇

✅ 1️⃣ Update README Clone URL (Important)

Inside your README, replace:
https://github.com/GANESH4459/real-time-notification-prioritizer.git

With:

https://github.com/GANESH4459/real-time-notification-prioritizer
### AI-Based Real-Time Notification Evaluation System

---

## 📌 Project Overview

The Smart Notification Prioritization Engine is a FastAPI-based backend system that evaluates incoming notifications and decides whether to:

- ✅ SEND  
- ⏳ DELAY  
- ❌ NEVER SEND  

The decision is made using rule-based logic that considers:

- Expiry time
- Exact duplicate detection
- Near duplicate detection
- User notification fatigue
- Priority-based scoring

This system is designed to reduce notification overload and improve user engagement quality.

---

## 🏗️ System Architecture

Incoming Notification  
        ↓  
Expiry Validation  
        ↓  
Exact Duplicate Check  
        ↓  
Near Duplicate Check  
        ↓  
Fatigue Analysis  
        ↓  
Score Computation  
        ↓  
Decision Classification  
        ↓  
Audit Logging  

---

## 🧠 Core Components

### 1️⃣ Notification Model

Defines the structure of incoming notifications using Pydantic:

- user_id (str)
- message (str)
- priority_hint (int)
- dedupe_key (str)
- expires_at (datetime, optional)

---

### 2️⃣ Expiry Validation

If `expires_at` exists and is earlier than the current UTC time:

→ Decision = **NEVER**

This prevents outdated notifications from being delivered.

---

### 3️⃣ Exact Duplicate Detection

Uses:
- user_id
- dedupe_key

If the same user has already received the same dedupe_key:

→ Decision = **NEVER**

Prevents repeated identical notifications.

---

### 4️⃣ Near Duplicate Detection

Uses simple text similarity logic:

If the new message is highly similar to previous messages:

→ Decision = **NEVER**

Prevents slightly modified repeated notifications.

---

### 5️⃣ User Fatigue Detection

Tracks user notification frequency.

If user receives too many notifications within a short period:

→ Fatigue = TRUE  
→ Score penalty applied

---

### 6️⃣ Score Computation

Score is calculated using:

Base Score = priority_hint  
- Fatigue penalty  
- Similarity penalty  

Final Score determines classification.

---

### 7️⃣ Decision Classification

| Score Range | Decision |
|-------------|----------|
| >= 70       | SEND     |
| 40 - 69     | DELAY    |
| < 40        | NEVER    |

---

### 8️⃣ Audit Logging

Every evaluated notification is logged with:

- notification_id
- decision
- score
- reason

Accessible via:

GET /audit

---

## 🔌 API Endpoints

### POST /notifications/evaluate

Evaluates a notification and returns:

```json
{
  "notification_id": "uuid",
  "decision": "SEND | DELAY | NEVER",
  "score": 75,
  "reason": "Priority=85, Fatigued=False"
}

⚙️ Execution Instructions
Install dependencies

pip install fastapi uvicorn pydantic

Run application

uvicorn main:app --reload

Open API Docs

http://127.0.0.1:8000/docs

📈 System Characteristics

✔ Real-time decision engine
✔ Lightweight and fast
✔ Modular logic
✔ Easily extendable
✔ Production scalable

🔮 Possible Enhancements

Redis-based caching

PostgreSQL integration

Machine Learning scoring model

Kafka-based event streaming

Rate limiting per user

Admin dashboard with analytics

🎯 Use Cases

E-commerce apps

Banking alerts

Healthcare reminders

Social media notifications

Marketing campaigns
