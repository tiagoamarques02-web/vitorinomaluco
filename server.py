from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "status": "MONSTER V4 PAPER TRADING"
    }

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    action = data.get("action")
    symbol = data.get("symbol")

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol}",
        flush=True
    )

    return jsonify({
        "success": True,
        "action": action,
        "symbol": symbol,
        "mode": "paper"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
