from flask import Flask, request, jsonify
from datetime import datetime
import hashlib
import hmac
import base64
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

def create_signature(timestamp, method, request_path):

    message = f"{timestamp}{method}{request_path}"

    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode()

    return signature

# =====================================================
# HEADERS
# =====================================================

def get_headers(method, path):

    timestamp = str(int(time.time() * 1000))

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": create_signature(timestamp, method, path),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER UTA TEST",
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE)
    })

# =====================================================
# UTA TEST
# =====================================================

@app.route("/uta-test")
def uta_test():

    return jsonify({
        "status": "uta-test-ok",
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

    print("=" * 60, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"PRICE={price} "
        f"TIMEFRAME={timeframe}",
        flush=True
    )

    print("=" * 60, flush=True)

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
