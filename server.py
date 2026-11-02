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

TRADE_QTY = "0.25"

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
# CURRENT POSITIONS
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
        "trade_qty": TRADE_QTY
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
# BUY TEST
# =====================================================

@app.route("/uta-buy-test")
def uta_buy_test():

    try:

        result = place_order(
            symbol="ZECUSDT",
            side="buy"
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# SELL TEST
# =====================================================

@app.route("/uta-sell-test")
def uta_sell_test():

    try:

        result = place_order(
            symbol="ZECUSDT",
            side="sell"
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# CLOSE LONG TEST
# =====================================================

@app.route("/uta-close-long")
def uta_close_long():

    try:

        result = close_position(
            symbol="ZECUSDT",
            pos_side="long"
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# CLOSE SHORT TEST
# =====================================================

@app.route("/uta-close-short")
def uta_close_short():

    try:

        result = close_position(
            symbol="ZECUSDT",
            pos_side="short"
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# TRADINGVIEW WEBHOOK
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

    try:

        if action == "LONG":

            result = place_order(
                symbol=symbol,
                side="buy"
            )

        elif action == "SHORT":

            result = place_order(
                symbol=symbol,
                side="sell"
            )

        elif action == "EXIT_LONG":

            result = close_position(
                symbol=symbol,
                pos_side="long"
            )

        elif action == "EXIT_SHORT":

            result = close_position(
                symbol=symbol,
                pos_side="short"
            )

        else:

            return jsonify({
                "success": False,
                "error": "unknown action"
            }), 400

        print(result, flush=True)

        print("=" * 70, flush=True)

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
