from flask import Flask, request, jsonify
from datetime import datetime
import hashlib
import hmac
import base64
import json
import time
import os
import requests

app = Flask(__name__)

# =====================================================
# CONFIG
# =====================================================

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

# =====================================================
# SIGNATURE
# =====================================================

def create_signature(timestamp, method, request_path, body=""):

    message = f"{timestamp}{method}{request_path}{body}"

    return base64.b64encode(
        hmac.new(
            API_SECRET.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode()

# =====================================================
# HEADERS
# =====================================================

def get_headers(method, path, body=""):

    timestamp = str(int(time.time() * 1000))

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": create_signature(timestamp, method, path, body),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US"
    }

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER UTA V3 TEST",
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE)
    })

# =====================================================
# POSITIONS
# =====================================================

@app.route("/uta-positions")
def uta_positions():

    try:

        path = "/api/v3/position/current-position?category=USDT-FUTURES"

        response = requests.get(
            BASE_URL + path,
            headers=get_headers("GET", path),
            timeout=20
        )

        return jsonify(response.json())

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# MAX OPEN AVAILABLE
# =====================================================

@app.route("/max-open")
def max_open():

    try:

        path = "/api/v3/account/max-open-available"

        body = {
            "category": "USDT-FUTURES",
            "symbol": "ZECUSDT",
            "orderType": "market",
            "side": "buy"
        }

        body_json = json.dumps(body)

        response = requests.post(
            BASE_URL + path,
            headers=get_headers("POST", path, body_json),
            data=body_json,
            timeout=20
        )

        return jsonify(response.json())

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)

    if not data:

        print("IGNORED EMPTY PAYLOAD", flush=True)

        return jsonify({
            "ignored": True
        }), 200

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price")
    timeframe = data.get("timeframe")

    print("=" * 70, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"PRICE={price} "
        f"TIMEFRAME={timeframe}",
        flush=True
    )

    print("=" * 70, flush=True)

    return jsonify({
        "success": True,
        "action": action,
        "symbol": symbol
    })

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
