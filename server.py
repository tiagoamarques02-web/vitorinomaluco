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

TRADE_QTY = "0.10"

CURRENT_POSITION = "FLAT"

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
# PLACE ORDER
# =====================================================

def place_order(symbol, side):

    path = "/api/v3/trade/place-order"

    body = {
        "category": "USDT-FUTURES",
        "symbol": symbol,
        "side": side,
        "orderType": "market",
        "qty": TRADE_QTY
    }

    body_json = json.dumps(body)

    response = requests.post(
        BASE_URL + path,
        headers=get_headers("POST", path, body_json),
        data=body_json,
        timeout=20
    )

    return response.json()

# =====================================================
# CLOSE POSITION
# =====================================================

def close_position(symbol, pos_side):

    path = "/api/v3/trade/close-positions"

    body = {
        "category": "USDT-FUTURES",
        "symbol": symbol,
        "posSide": pos_side
    }

    body_json = json.dumps(body)

    response = requests.post(
        BASE_URL + path,
        headers=get_headers("POST", path, body_json),
        data=body_json,
        timeout=20
    )

    return response.json()

# =====================================================
# GET POSITIONS
# =====================================================

def get_positions():

    path = "/api/v3/position/current-position?category=USDT-FUTURES"

    response = requests.get(
        BASE_URL + path,
        headers=get_headers("GET", path),
        timeout=20
    )

    return response.json()

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER UTA V3 LIVE",
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE),
        "trade_qty": TRADE_QTY,
        "current_position": CURRENT_POSITION
    })

# =====================================================
# POSITIONS
# =====================================================

@app.route("/uta-positions")
def uta_positions():

    try:
        return jsonify(get_positions())

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

    global CURRENT_POSITION

    data = request.get_json(silent=True)

    if not data:

        print("IGNORED EMPTY PAYLOAD", flush=True)

        return jsonify({
            "ignored": True
        }), 200

    action = data.get("action")
    symbol = data.get("symbol")

    print("=" * 80, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"CURRENT_POSITION={CURRENT_POSITION}",
        flush=True
    )

    try:

        # =====================================================
        # LONG
        # =====================================================

        if action == "LONG":

            if CURRENT_POSITION == "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "already_long"
                })

            result = place_order(
                symbol=symbol,
                side="buy"
            )

            CURRENT_POSITION = "LONG"

        # =====================================================
        # SHORT
        # =====================================================

        elif action == "SHORT":

            if CURRENT_POSITION == "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "already_short"
                })

            result = place_order(
                symbol=symbol,
                side="sell"
            )

            CURRENT_POSITION = "SHORT"

        # =====================================================
        # EXIT LONG
        # =====================================================

        elif action == "EXIT_LONG":

            if CURRENT_POSITION != "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "no_long_position"
                })

            result = close_position(
                symbol=symbol,
                pos_side="long"
            )

            CURRENT_POSITION = "FLAT"

        # =====================================================
        # EXIT SHORT
        # =====================================================

        elif action == "EXIT_SHORT":

            if CURRENT_POSITION != "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "no_short_position"
                })

            result = close_position(
                symbol=symbol,
                pos_side="short"
            )

            CURRENT_POSITION = "FLAT"

        else:

            return jsonify({
                "success": False,
                "error": "unknown action"
            }), 400

        print(result, flush=True)

        print(
            f"NEW_POSITION={CURRENT_POSITION}",
            flush=True
        )

        print("=" * 80, flush=True)

        return jsonify({
            "success": True,
            "action": action,
            "symbol": symbol,
            "position": CURRENT_POSITION,
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
