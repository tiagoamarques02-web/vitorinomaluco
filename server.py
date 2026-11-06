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

def create_signature(timestamp, method, path, body=""):

    message = f"{timestamp}{method}{path}{body}"

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

def get_headers(method, path, body=""):

    timestamp = str(int(time.time() * 1000))

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": create_signature(
            timestamp,
            method,
            path,
            body
        ),
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
        "locale": "en-US"
    }

# =====================================================
# POSIÇÃO REAL BITGET
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
                .get("list", [])
        )

        if not positions:
            return "FLAT"

        for pos in positions:

            qty = float(
                pos.get("total", "0")
            )

            if qty <= 0:
                continue

            side = str(
                pos.get("posSide", "")
            ).lower()

            if side == "long":
                return "LONG"

            if side == "short":
                return "SHORT"

        return "FLAT"

    except Exception as e:

        print(
            f"GET POSITION ERROR: {e}",
            flush=True
        )

        return "FLAT"

# =====================================================
# ESPERAR FECHO TOTAL
# =====================================================

def wait_flat(symbol, timeout=20):

    start = time.time()

    while time.time() - start < timeout:

        current = get_real_position(symbol)

        if current == "FLAT":
            return True

        time.sleep(1)

    return False

# =====================================================
# ABRIR ORDEM
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

    body_json = json.dumps(
        body,
        separators=(",", ":")
    )

    response = requests.post(
        BASE_URL + path,
        headers=get_headers(
            "POST",
            path,
            body_json
        ),
        data=body_json,
        timeout=20
    )

    return response.json()

# =====================================================
# FECHAR POSIÇÃO
# =====================================================

def close_position(symbol, pos_side):

    path = "/api/v3/trade/close-positions"

    body = {
        "category": "USDT-FUTURES",
        "symbol": symbol,
        "posSide": pos_side
    }

    body_json = json.dumps(
        body,
        separators=(",", ":")
    )

    response = requests.post(
        BASE_URL + path,
        headers=get_headers(
            "POST",
            path,
            body_json
        ),
        data=body_json,
        timeout=20
    )

    return response.json()

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER LIVE",
        "trade_qty": TRADE_QTY,
        "api_key": bool(API_KEY),
        "secret": bool(API_SECRET),
        "passphrase": bool(PASSPHRASE)
    })

# =====================================================
# POSIÇÕES
# =====================================================

@app.route("/uta-positions")
def uta_positions():

    try:

        path = (
            "/api/v3/position/current-position"
            "?category=USDT-FUTURES"
        )

        response = requests.get(
            BASE_URL + path,
            headers=get_headers(
                "GET",
                path
            ),
            timeout=20
        )

        return jsonify(
            response.json()
        )

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

        return jsonify({
            "ignored": True,
            "reason": "empty_payload"
        }), 200

    action = data.get("action")
    symbol = data.get("symbol")

    if not symbol:

        return jsonify({
            "success": False,
            "error": "missing_symbol"
        }), 400

    current_position = get_real_position(symbol)

    print("=" * 80, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"POSITION={current_position}",
        flush=True
    )

    try:

        # =================================================
        # LONG
        # =================================================

        if action == "LONG":

            if current_position == "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "already_long"
                })

            if current_position == "SHORT":

                close_position(
                    symbol,
                    "short"
                )

                if not wait_flat(symbol):

                    return jsonify({
                        "success": False,
                        "error": "timeout_waiting_short_close"
                    }), 500

            result = place_order(
                symbol,
                "buy"
            )

        # =================================================
        # SHORT
        # =================================================

        elif action == "SHORT":

            if current_position == "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "already_short"
                })

            if current_position == "LONG":

                close_position(
                    symbol,
                    "long"
                )

                if not wait_flat(symbol):

                    return jsonify({
                        "success": False,
                        "error": "timeout_waiting_long_close"
                    }), 500

            result = place_order(
                symbol,
                "sell"
            )

        # =================================================
        # EXIT LONG
        # =================================================

        elif action == "EXIT_LONG":

            if current_position != "LONG":

                return jsonify({
                    "ignored": True,
                    "reason": "no_long_position"
                })

            result = close_position(
                symbol,
                "long"
            )

        # =================================================
        # EXIT SHORT
        # =================================================

        elif action == "EXIT_SHORT":

            if current_position != "SHORT":

                return jsonify({
                    "ignored": True,
                    "reason": "no_short_position"
                })

            result = close_position(
                symbol,
                "short"
            )

        else:

            return jsonify({
                "success": False,
                "error": "unknown_action"
            }), 400

        print(result, flush=True)
        print("=" * 80, flush=True)

        return jsonify({
            "success": True,
            "action": action,
            "symbol": symbol,
            "position_before": current_position,
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
