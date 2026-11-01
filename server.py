from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "online"
    })

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True) or {}

    action = data.get("action")
    symbol = data.get("symbol")

    print(
        f"[{datetime.now()}] ACTION={action} SYMBOL={symbol}",
        flush=True
    )

    return jsonify({
        "success": True
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
