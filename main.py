from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import difflib

app = FastAPI(title="Advanced Notification Prioritization Engine")

# =========================================================
# CONFIGURABLE RULES (Human Editable)
# =========================================================

RULES = {
    "daily_limit": 5,
    "cooldown_seconds": 120,
    "high_priority_threshold": 80,
    "medium_priority_threshold": 50,
    "similarity_threshold": 0.85
}

# =========================================================
# IN-MEMORY STORES
# =========================================================

exact_store = set()
recent_messages = []
user_history = {}
deferred_queue = []
audit_logs = []

metrics = {
    "NOW": 0,
    "LATER": 0,
    "NEVER": 0,
    "duplicates_blocked": 0,
    "fatigue_delays": 0,
    "fallback_triggered": 0
}

# =========================================================
# DATA MODEL
# =========================================================

class NotificationEvent(BaseModel):
    user_id: str
    event_type: str
    message: str
    channel: str = "push"
    priority_hint: int = 50
    dedupe_key: str | None = None
    expires_at: datetime | None = None


# =========================================================
# DUPLICATE HANDLING
# =========================================================

def exact_duplicate(user_id, dedupe_key):
    if not dedupe_key:
        return False
    key = f"{user_id}:{dedupe_key}"
    if key in exact_store:
        return True
    exact_store.add(key)
    return False


def near_duplicate(message):
    for old_msg in recent_messages:
        similarity = difflib.SequenceMatcher(None, message, old_msg).ratio()
        if similarity > RULES["similarity_threshold"]:
            return True
    recent_messages.append(message)
    return False


# =========================================================
# FATIGUE LOGIC
# =========================================================

def is_fatigued(user_id):
    history = user_history.get(user_id, [])
    now = datetime.now(timezone.utc)

    history = [t for t in history if (now - t).seconds < RULES["cooldown_seconds"]]
    user_history[user_id] = history

    return len(history) >= RULES["daily_limit"]


def update_user_history(user_id):
    user_history.setdefault(user_id, []).append(datetime.now(timezone.utc))


# =========================================================
# SCORING & CLASSIFICATION
# =========================================================

def compute_score(event, fatigued):
    try:
        score = event.priority_hint

        # Channel Weight
        channel_weight = {
            "sms": 15,
            "push": 10,
            "email": 5
        }.get(event.channel, 0)

        score += channel_weight

        # System Alert Boost
        if event.event_type == "system_alert":
            score += 20

        # Fatigue penalty
        if fatigued:
            score -= 15

        return max(0, min(score, 100))

    except:
        metrics["fallback_triggered"] += 1
        return event.priority_hint or 50


def classify(event, score, fatigued):

    # Conflict Handling: urgent but fatigued
    if fatigued and score < RULES["high_priority_threshold"]:
        metrics["fatigue_delays"] += 1
        return "LATER"

    if score >= RULES["high_priority_threshold"]:
        return "NOW"

    if score >= RULES["medium_priority_threshold"]:
        return "LATER"

    return "NEVER"


# =========================================================
# AUDIT
# =========================================================

def log_decision(notification_id, decision, score, reason):
    audit_logs.append({
        "notification_id": notification_id,
        "decision": decision,
        "score": score,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc)
    })


# =========================================================
# ROUTES
# =========================================================

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/audit")
def get_audit():
    return audit_logs


@app.get("/metrics")
def get_metrics():
    return metrics


@app.get("/deferred")
def get_deferred():
    return deferred_queue


@app.post("/notifications/evaluate")
def evaluate(event: NotificationEvent):

    notification_id = str(uuid4())

    # 1️⃣ Expiry Check
    if event.expires_at:
        expires_at = event.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            metrics["NEVER"] += 1
            log_decision(notification_id, "NEVER", 0, "Expired notification")
            return {
                "notification_id": notification_id,
                "decision": "NEVER",
                "score": 0,
                "reason": "Expired notification"
            }

    # 2️⃣ Exact Duplicate
    if exact_duplicate(event.user_id, event.dedupe_key):
        metrics["duplicates_blocked"] += 1
        log_decision(notification_id, "NEVER", 0, "Exact duplicate")
        return {
            "notification_id": notification_id,
            "decision": "NEVER",
            "score": 0,
            "reason": "Exact duplicate"
        }

    # 3️⃣ Near Duplicate
    if near_duplicate(event.message):
        metrics["duplicates_blocked"] += 1
        log_decision(notification_id, "NEVER", 0, "Near duplicate")
        return {
            "notification_id": notification_id,
            "decision": "NEVER",
            "score": 0,
            "reason": "Near duplicate"
        }

    # 4️⃣ Fatigue
    fatigued = is_fatigued(event.user_id)

    # 5️⃣ Compute Score
    score = compute_score(event, fatigued)

    # 6️⃣ Final Classification
    decision = classify(event, score, fatigued)

    # 7️⃣ Deferred Handling
    if decision == "LATER":
        deferred_queue.append({
            "notification_id": notification_id,
            "event": event.dict()
        })

    update_user_history(event.user_id)
    metrics[decision] += 1

    reason = f"Priority={event.priority_hint}, Channel={event.channel}, Fatigued={fatigued}, Score={score}"

    log_decision(notification_id, decision, score, reason)

    return {
        "notification_id": notification_id,
        "decision": decision,
        "score": score,
        "reason": reason
    }