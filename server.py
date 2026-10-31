from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# =====================================================
# CONFIG
# =====================================================

API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return jsonify({
        "status": "MONSTER V9 TEST MODE",
        "api_key_loaded": bool(API_KEY),
        "secret_loaded": bool(API_SECRET),
        "passphrase_loaded": bool(PASSPHRASE),
        "real_trading": False
    })

# =====================================================
# HEALTH
# =====================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })

# =====================================================
# WEBHOOK
# =====================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    action = data.get("action", "")
    symbol = data.get("symbol", "")
    price = data.get("price", "")
    timeframe = data.get("timeframe", "")

    print("=" * 70, flush=True)

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol} "
        f"PRICE={price} "
        f"TIMEFRAME={timeframe}",
        flush=True
    )

    if action == "LONG":
        print("TEST MODE -> OPEN LONG", flush=True)

    elif action == "SHORT":
        print("TEST MODE -> OPEN SHORT", flush=True)

    elif action == "EXIT_LONG":
        print("TEST MODE -> CLOSE LONG", flush=True)

    elif action == "EXIT_SHORT":
        print("TEST MODE -> CLOSE SHORT", flush=True)

    else:
        print(f"UNKNOWN ACTION -> {action}", flush=True)

    print("=" * 70, flush=True)

    return jsonify({
        "success": True,
        "mode": "test",
        "action": action,
        "symbol": symbol,
        "price": price,
        "timeframe": timeframe,
        "timestamp": str(datetime.now())
    })

# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
