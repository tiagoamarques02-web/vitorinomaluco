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

TRADE_QTY = "0.01"

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
# POSIÇÃO REAL
# =====================================================

def get_real_position(symbol):

    try:

        path = (
            "/api/v3/position/current-position"
            f"?category=USDT-FUTURES&symbol={symbol}"
        )

        response = requests.get(
            BASE_URL + path,
            headers=get_headers("GET", path),
            timeout=20
        )

        data = response.json()

        positions = (
            data.get("data", {})
                .get("list")
        )

        if not positions:
            return "FLAT"

        for pos in positions:

            side = str(
                pos.get("posSide", "")
            ).lower()

            qty = float(
                pos.get("total", "0")
            )

            if qty <= 0:
                continue

            if side == "long":
                return "LONG"

            if side == "short":
                return "SHORT"

        return "FLAT"

    except Exception as e:

        print(
            f"POSITION ERROR: {e}",
            flush=True
        )

        return "FLAT"

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
# POSITIONS ENDPOINT
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
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER UTA V3 LIVE",
        "trade_qty": TRADE_QTY,
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE)
    })

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)

    if not data:

        print(
            "IGNORED EMPTY PAYLOAD",
            flush=True
        )

        return jsonify({
            "ignored": True
        }), 200

    action = data.get("action")
    symbol = data.get("symbol")

    current_position = get_real_position(symbol)

    print("=" * 80, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"REAL_POSITION={current_position}",
        flush=True
    )

    try:

        # ==========================================
        # LONG
        # ==========================================

        if action == "LONG":

            if current_position == "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "already_long"
                })

            result = place_order(
                symbol=symbol,
                side="buy"
            )

        # ==========================================
        # SHORT
        # ==========================================

        elif action == "SHORT":

            if current_position == "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "already_short"
                })

            result = place_order(
                symbol=symbol,
                side="sell"
            )

        # ==========================================
        # EXIT LONG
        # ==========================================

        elif action == "EXIT_LONG":

            if current_position != "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "no_long_position"
                })

            result = close_position(
                symbol=symbol,
                pos_side="long"
            )

        # ==========================================
        # EXIT SHORT
        # ==========================================

        elif action == "EXIT_SHORT":

            if current_position != "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "no_short_position"
                })

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

        print("=" * 80, flush=True)

        return jsonify({
            "success": True,
            "action": action,
            "symbol": symbol,
            "real_position_before": current_position,
            "result": result
        })

    except Exception as e:

        print(
            f"ERROR: {e}",
            flush=True
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
