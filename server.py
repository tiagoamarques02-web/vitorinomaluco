from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# =====================================================
# CONFIG
# =====================================================

DRY_RUN = True

TRADE_QTY = "0.01"

# =====================================================
# ESTADO SIMULADO
# =====================================================

SIM_POSITION = "FLAT"

# =====================================================
# POSITION
# =====================================================

def get_real_position(symbol):

    global SIM_POSITION

    print(
        f"[DRY RUN] POSITION CHECK {symbol} -> {SIM_POSITION}",
        flush=True
    )

    return SIM_POSITION

# =====================================================
# PLACE ORDER
# =====================================================

def place_order(symbol, side):

    global SIM_POSITION

    if side == "buy":
        SIM_POSITION = "LONG"

    elif side == "sell":
        SIM_POSITION = "SHORT"

    result = {
        "success": True,
        "dry_run": True,
        "operation": "OPEN",
        "symbol": symbol,
        "side": side,
        "position_after": SIM_POSITION,
        "timestamp": str(datetime.now())
    }

    print(result, flush=True)

    return result

# =====================================================
# CLOSE POSITION
# =====================================================

def close_position(symbol, pos_side):

    global SIM_POSITION

    SIM_POSITION = "FLAT"

    result = {
        "success": True,
        "dry_run": True,
        "operation": "CLOSE",
        "symbol": symbol,
        "posSide": pos_side,
        "position_after": SIM_POSITION,
        "timestamp": str(datetime.now())
    }

    print(result, flush=True)

    return result

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER DRY RUN",
        "dry_run": DRY_RUN,
        "trade_qty": TRADE_QTY,
        "simulated_position": SIM_POSITION
    })

# =====================================================
# POSITION STATUS
# =====================================================

@app.route("/uta-positions")
def uta_positions():

    return jsonify({
        "success": True,
        "dry_run": True,
        "position": SIM_POSITION
    })

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    global SIM_POSITION

    data = request.get_json(silent=True)

    if not data:

        return jsonify({
            "ignored": True,
            "reason": "empty_payload"
        }), 200

    action = str(
        data.get("action", "")
    ).upper()

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

            result = place_order(
                symbol,
                "sell"
            )

        # =================================================
        # EXIT LONG
        # =================================================

        elif action in ["EXIT_LONG", "LX"]:

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

        elif action in ["EXIT_SHORT", "SX"]:

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
                "error": "unknown_action",
                "received": action
            }), 400

        print(result, flush=True)
        print("=" * 80, flush=True)

        return jsonify({
            "success": True,
            "dry_run": True,
            "action": action,
            "symbol": symbol,
            "position_before": current_position,
            "position_after": SIM_POSITION,
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
# HEALTH
# =====================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "dry_run": True,
        "position": SIM_POSITION,
        "timestamp": str(datetime.now())
    })

# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
