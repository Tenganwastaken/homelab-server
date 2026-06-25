"""
Bot Control API — Flask REST API for managing Discord bots via HTTP.
Endpoints:
  GET  /status          — Returns running status of all bots
  POST /restart/<bot>   — Restarts a specific bot by name
        bot = "discordbot" | "skinpeek"

Used by Homepage dashboard widgets or any HTTP client.
Runs as a systemd service on port 9999.
"""

import subprocess
from flask import Flask, jsonify, abort

app = Flask(__name__)

# Systemd service names for each bot
BOTS = {
    "discordbot": "discordbot",
    "skinpeek": "skinpeek",
}


def get_service_status(service_name: str) -> str:
    """Returns 'active', 'inactive', 'failed', or 'unknown'."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"


def restart_service(service_name: str) -> bool:
    """Restarts a systemd service. Returns True on success."""
    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


@app.route("/status", methods=["GET"])
def status():
    """Return the running status of all bots."""
    statuses = {
        name: get_service_status(service)
        for name, service in BOTS.items()
    }
    return jsonify(statuses)


@app.route("/restart/<bot_name>", methods=["POST"])
def restart(bot_name: str):
    """Restart a specific bot by name."""
    if bot_name not in BOTS:
        abort(404, description=f"Unknown bot: '{bot_name}'. Valid: {list(BOTS.keys())}")

    service = BOTS[bot_name]
    success = restart_service(service)

    if success:
        return jsonify({"status": "restarted", "bot": bot_name}), 200
    else:
        return jsonify({"status": "error", "bot": bot_name, "message": "restart failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
