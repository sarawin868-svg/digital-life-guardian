from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


# ============================================
# SECURITY ACTIVITY LOG
# ============================================

activity_logs = []


def add_activity(message, level="info"):

    activity_logs.insert(
        0,
        {
            "message": message,
            "level": level,
            "time": datetime.now().strftime("%I:%M:%S %p")
        }
    )

    # Keep only latest 50 activities
    if len(activity_logs) > 50:
        activity_logs.pop()


# ============================================
# HOME
# ============================================

@app.route("/")
def home():

    return "Digital Life Guardian Backend Connected!"


# ============================================
# BACKEND STATUS
# ============================================

@app.route("/api/status")
def api_status():

    return jsonify({
        "status": "online",
        "message": "Digital Life Guardian is active"
    })


# ============================================
# SECURITY STATUS
# ============================================

@app.route("/api/security")
def security_status():

    add_activity(
        "Security status checked",
        "success"
    )

    return jsonify({
        "alert": False,
        "message": "No suspicious activity detected",
        "level": "Normal"
    })


# ============================================
# ACTIVITY LOG
# ============================================

@app.route("/api/activity")
def get_activity():

    return jsonify({
        "activities": activity_logs
    })


# ============================================
# ADD ACTIVITY
# ============================================

@app.route("/api/activity", methods=["POST"])
def create_activity():

    data = request.get_json() or {}

    message = data.get(
        "message",
        "Unknown activity"
    )

    level = data.get(
        "level",
        "info"
    )

    add_activity(
        message,
        level
    )

    return jsonify({
        "success": True,
        "message": "Activity recorded"
    })


# ============================================
# RISK SCORE
# ============================================

@app.route("/api/risk-score", methods=["POST"])
def risk_score():

    data = request.get_json() or {}

    expiring_count = int(
        data.get("expiringCount", 0)
    )

    expired_count = int(
        data.get("expiredCount", 0)
    )

    security_alert = bool(
        data.get("securityAlert", False)
    )

    document_count = int(
        data.get("documentCount", 0)
    )


    # Start with maximum safety
    score = 100


    # Expiring documents
    score -= expiring_count * 5


    # Expired documents
    score -= expired_count * 15


    # Security alert
    if security_alert:
        score -= 30


    # No documents is slightly risky
    if document_count == 0:
        score -= 5


    # Keep score between 0 and 100
    score = max(
        0,
        min(
            100,
            score
        )
    )


    if score >= 80:

        status = "Safe"
        level = "safe"

    elif score >= 50:

        status = "Attention Required"
        level = "warning"

    else:

        status = "High Risk"
        level = "danger"


    return jsonify({

        "score": score,

        "status": status,

        "level": level

    })


# ============================================
# GUARDIAN AI
# ============================================

@app.route(
    "/api/guardian",
    methods=["POST"]
)
def guardian():

    data = request.get_json() or {}

    question = data.get(
        "question",
        ""
    ).lower().strip()


    document_names = data.get(
        "documentNames",
        []
    )

    expiring_documents = data.get(
        "expiringDocuments",
        []
    )

    expired_documents = data.get(
        "expiredDocuments",
        []
    )

    valid_documents = data.get(
        "validDocuments",
        []
    )

    no_expiry_documents = data.get(
        "noExpiryDocuments",
        []
    )


    # ========================================
    # LOG GUARDIAN QUERY
    # ========================================

    add_activity(
        "Guardian received a new request",
        "info"
    )


    # ========================================
    # GREETING
    # ========================================

    if (
        "hello" in question
        or "hi" in question
        or "hey" in question
    ):

        reply = (
            "👋 Hello! I'm your Digital Life Guardian. "
            "I can monitor your documents, expiry dates, "
            "security status and activity."
        )


    # ========================================
    # DOCUMENT COUNT
    # ========================================

    elif (
        "how many" in question
        and "document" in question
    ):

        count = len(document_names)

        reply = (
            f"📄 You currently have "
            f"{count} document"
            f"{'s' if count != 1 else ''}."
        )


    # ========================================
    # EXPIRING DOCUMENTS
    # ========================================

    elif (
        "expiring" in question
        or "expire soon" in question
        or "expir" in question
    ):

        if expiring_documents:

            reply = (
                "🟠 Documents expiring soon:\n\n"
                + "\n".join(
                    "• " + name
                    for name in expiring_documents
                )
            )

        else:

            reply = (
                "🟢 You don't have any "
                "documents expiring within "
                "the next 30 days."
            )


    # ========================================
    # EXPIRED DOCUMENTS
    # ========================================

    elif "expired" in question:

        if expired_documents:

            reply = (
                "🔴 Expired documents:\n\n"
                + "\n".join(
                    "• " + name
                    for name in expired_documents
                )
            )

        else:

            reply = (
                "🟢 You don't have any "
                "expired documents."
            )


    # ========================================
    # VALID DOCUMENTS
    # ========================================

    elif (
        "valid" in question
        or "safe document" in question
    ):

        if valid_documents:

            reply = (
                "🟢 Valid documents:\n\n"
                + "\n".join(
                    "• " + name
                    for name in valid_documents
                )
            )

        else:

            reply = (
                "ℹ️ There are currently "
                "no documents marked as valid."
            )


    # ========================================
    # ALL DOCUMENTS
    # ========================================

    elif "document" in question:

        if document_names:

            reply = (
                "📂 Your documents:\n\n"
                + "\n".join(
                    "• " + name
                    for name in document_names
                )
            )

        else:

            reply = (
                "📂 No documents have "
                "been uploaded yet."
            )


    # ========================================
    # SECURITY
    # ========================================

    elif (
        "security" in question
        or "secure" in question
    ):

        reply = (
            "🛡️ Your current security "
            "status is NORMAL. "
            "No suspicious activity "
            "has been detected."
        )


    # ========================================
    # RISK
    # ========================================

    elif (
        "risk" in question
        or "score" in question
    ):

        expiring = len(
            expiring_documents
        )

        expired = len(
            expired_documents
        )


        score = 100

        score -= expiring * 5
        score -= expired * 15

        score = max(
            0,
            min(
                100,
                score
            )
        )


        if score >= 80:

            status = "Safe 🟢"

        elif score >= 50:

            status = "Attention Required 🟠"

        else:

            status = "High Risk 🔴"


        reply = (
            f"🛡️ Your current security "
            f"risk score is {score}/100.\n\n"
            f"Status: {status}"
        )


    # ========================================
    # ACTIVITY
    # ========================================

    elif (
        "activity" in question
        or "monitor" in question
    ):

        reply = (
            "📊 Guardian is actively monitoring "
            "your digital environment."
        )


    # ========================================
    # HELP
    # ========================================

    elif (
        "help" in question
        or "what can you do" in question
    ):

        reply = (
            "🤖 I can help you with:\n\n"
            "📄 Documents\n"
            "⏰ Expiry dates\n"
            "🔴 Expired documents\n"
            "🛡️ Security status\n"
            "📊 Risk score\n"
            "📈 Activity monitoring"
        )


    # ========================================
    # DEFAULT
    # ========================================

    else:

        reply = (
            "🤖 I can currently help with "
            "documents, expiry dates, "
            "security, risk score and "
            "activity monitoring."
        )


    return jsonify({
        "reply": reply
    })


# ============================================
# START SERVER
# ============================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("   DIGITAL LIFE GUARDIAN BACKEND")
    print("======================================")
    print("Backend Started Successfully!")
    print()

    add_activity(
        "Guardian backend started",
        "success"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )