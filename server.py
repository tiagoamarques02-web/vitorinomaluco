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

POSITION_SIZE_USDT = 5
LEVERAGE = 3

# =====================================================
# SIGNATURE
# =====================================================

def sign(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"

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

def headers(method, path, body=""):
    timestamp = str(int(time.time() * 1000))

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign(timestamp, method, path, body),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US"
    }

# =====================================================
# ORDER
# =====================================================

def place_order(symbol, side):

    path = "/api/v2/mix/order/place-order"

    body = {
        "symbol": symbol,
        "productType": "USDT-FUTURES",
        "marginMode": "isolated",
        "marginCoin": "USDT",
        "size": str(POSITION_SIZE_USDT),
        "side": side,
        "orderType": "market"
    }

    body_json = json.dumps(body)

    response = requests.post(
        BASE_URL + path,
        headers=headers("POST", path, body_json),
        data=body_json,
        timeout=15
    )

    print(response.text, flush=True)

    return response.json()

# =====================================================
# CLOSE
# =====================================================

def close_position(symbol, hold_side):

    path = "/api/v2/mix/order/close-positions"

    body = {
        "symbol": symbol,
        "productType": "USDT-FUTURES",
        "holdSide": hold_side
    }

    body_json = json.dumps(body)

    response = requests.post(
        BASE_URL + path,
        headers=headers("POST", path, body_json),
        data=body_json,
        timeout=15
    )

    print(response.text, flush=True)

    return response.json()

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER V9 REAL",
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE),
        "size_usdt": POSITION_SIZE_USDT,
        "leverage": LEVERAGE
    })

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    action = data.get("action")
    symbol = data.get("symbol")

    print("=" * 60, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol}",
        flush=True
    )

    try:

        if action == "LONG":

            close_position(symbol, "short")
            result = place_order(symbol, "buy")

        elif action == "SHORT":

            close_position(symbol, "long")
            result = place_order(symbol, "sell")

        elif action == "EXIT_LONG":

            result = close_position(symbol, "long")

        elif action == "EXIT_SHORT":

            result = close_position(symbol, "short")

        else:

            return jsonify({
                "success": False,
                "error": "unknown action"
            }), 400

        print(result, flush=True)

        return jsonify({
            "success": True,
            "action": action,
            "symbol": symbol,
            "result": result
        })

    except Exception as e:

        print(str(e), flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
