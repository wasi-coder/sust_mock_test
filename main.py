from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Literal

app = FastAPI()

# --- 1. Define Strict Input Schema ---
class TicketRequest(BaseModel):
    ticket_id: str
    channel: Optional[str] = None
    locale: Optional[str] = None
    message: str

# --- 2. Define Strict Output Schema ---
class TicketResponse(BaseModel):
    ticket_id: str
    case_type: Literal["wrong_transfer", "payment_failed", "refund_request", "phishing_or_social_engineering", "other"]
    severity: Literal["low", "medium", "high", "critical"]
    department: Literal["customer_support", "dispute_resolution", "payments_ops", "fraud_risk"]
    agent_summary: str
    human_review_required: bool
    confidence: float

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/sort-ticket", response_model=TicketResponse)
def sort_ticket(ticket: TicketRequest):
    message = ticket.message.lower()

    # Defaults matching the 'other' category
    case_type = "other"
    severity = "low"
    department = "customer_support"
    # Pre-written summary prevents accidentally echoing back a PIN/OTP
    agent_summary = "Customer reported a general issue requiring support."

    # Rule-based routing
    if "wrong" in message and "sent" in message:
        case_type = "wrong_transfer"
        severity = "high"
        department = "dispute_resolution"
        agent_summary = "Customer reports sending funds to an incorrect number."

    elif "failed" in message or "deducted" in message:
        case_type = "payment_failed"
        severity = "high"
        department = "payments_ops"
        agent_summary = "Customer states transaction failed but balance may be deducted."

    elif "refund" in message:
        case_type = "refund_request"
        severity = "low"
        department = "customer_support"
        agent_summary = "Customer is requesting a refund for a previous transaction."

    elif any(word in message for word in ["otp", "pin", "password", "scam"]):
        case_type = "phishing_or_social_engineering"
        severity = "critical"
        department = "fraud_risk"
        agent_summary = "Security risk flagged: Suspicious activity regarding user credentials."

    # The PDF requires human_review_required to be true for phishing or critical severity
    human_review = severity == "critical" or case_type == "phishing_or_social_engineering"

    return {
        "ticket_id": ticket.ticket_id,
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": agent_summary,
        "human_review_required": human_review,
        "confidence": 0.85
    }