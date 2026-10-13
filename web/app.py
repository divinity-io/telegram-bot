import hashlib
import hmac
import json
import os
import time
from urllib.parse import parse_qsl

from flask import Flask, jsonify, render_template, request

from config import BOT_TOKEN
from database import get_user, get_tool_history

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

MAX_AUTH_AGE = 3600


def verify_telegram_init_data(init_data):
    """Verify Telegram Mini App initData using the bot token."""
    if not BOT_TOKEN or not init_data:
        return None

    try:
        pairs = parse_qsl(init_data, keep_blank_values=True)
        data = dict(pairs)

        # Duplicate keys must not be accepted.
        if len(data) != len(pairs):
            return None

        received_hash = data.pop("hash", None)
        if not received_hash:
            return None

        auth_date = int(data.get("auth_date", "0"))
        now = int(time.time())

        if auth_date > now + 30 or now - auth_date > MAX_AUTH_AGE:
            return None

        data_check_string = "\n".join(
            f"{key}={value}"
            for key, value in sorted(data.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            return None

        user_data = json.loads(data.get("user", "{}"))
        telegram_id = user_data.get("id")

        if not isinstance(telegram_id, int) or isinstance(telegram_id, bool):
            return None

        return telegram_id

    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def authenticated_telegram_id():
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("tma "):
        return None

    return verify_telegram_init_data(authorization[4:].strip())


@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/api/me")
def my_dashboard_data():
    telegram_id = authenticated_telegram_id()

    if telegram_id is None:
        return jsonify({"error": "Telegram authentication failed"}), 401

    try:
        profiles = get_user(telegram_id)

        if not profiles:
            return jsonify({"error": "No registered DCORE account found"}), 404

        profile = profiles[0]
        history = get_tool_history(telegram_id, 10) or []

        # Return only the fields required by the dashboard.
        safe_profile = {
            "first_name": profile.get("first_name"),
            "username": profile.get("username"),
            "language": profile.get("language", "English"),
            "notifications": profile.get("notifications"),
        }

        safe_history = [
            {
                "tool_name": item.get("tool_name"),
                "created_at": item.get("created_at"),
            }
            for item in history
        ]

        return jsonify({
            "profile": safe_profile,
            "history": safe_history,
        })

    except Exception:
        app.logger.exception("Failed to load DCORE dashboard data")
        return jsonify({"error": "Dashboard data is temporarily unavailable"}), 500


if __name__ == "__main__":
    # Local testing only. Use a production WSGI server when deployed.
    app.run(host="127.0.0.1", port=5000, debug=False)
