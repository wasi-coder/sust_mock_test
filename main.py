from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/sort-ticket")
def sort_ticket(ticket: dict):

    message = ticket["message"].lower()

    case_type = "other"
    severity = "low"
    department = "customer_support"

    if "wrong" in message and "sent" in message:
        case_type = "wrong_transfer"
        severity = "high"
        department = "dispute_resolution"

    elif "failed" in message or "balance deducted" in message:
        case_type = "payment_failed"
        severity = "high"
        department = "payments_ops"

    elif "refund" in message:
        case_type = "refund_request"
        severity = "low"
        department = "customer_support"

    elif any(word in message for word in ["otp", "pin", "password"]):
        case_type = "phishing_or_social_engineering"
        severity = "critical"
        department = "fraud_risk"

    return {
        "ticket_id": ticket["ticket_id"],
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": f"Customer reports: {ticket['message']}",
        "human_review_required":
            severity == "critical" or
            case_type == "phishing_or_social_engineering",
        "confidence": 0.85
    }