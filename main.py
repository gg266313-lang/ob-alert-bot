import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload, timeout=10)
    return response.ok

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw = request.data.decode("utf-8")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"message": raw}

        direction = data.get("direction", "").upper()
        stars     = int(data.get("stars", 0))
        ticker    = data.get("ticker", "N/A")
        timeframe = data.get("timeframe", "N/A")
        price     = data.get("price", "N/A")

        if stars < 4:
            return jsonify({"status": "ignored", "reason": f"stars={stars} < 4"}), 200

        emoji = "🟢" if direction == "BULL" else "🔴"
        dir_label = "Bullish" if direction == "BULL" else "Bearish"
        star_str = "⭐" * stars

        message = (
            f"{emoji} <b>Order Block Alert</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Symbol:</b> {ticker}\n"
            f"⏱ <b>Timeframe:</b> {timeframe}\n"
            f"📈 <b>Direction:</b> {dir_label}\n"
            f"💰 <b>Price:</b> {price}\n"
            f"🌟 <b>Stars:</b> {star_str} ({stars}/5)\n"
            f"━━━━━━━━━━━━━━━━"
        )

        ok = send_telegram(message)
        if ok:
            return jsonify({"status": "sent"}), 200
        else:
            return jsonify({"status": "telegram_error"}), 500

    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
