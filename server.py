from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "online"
    })

@app.route("/uta-test")
def uta_test():
    return jsonify({
        "status": "uta-test-ok",
        "api_key": bool(os.getenv("BITGET_API_KEY")),
        "secret": bool(os.getenv("BITGET_API_SECRET")),
        "passphrase": bool(os.getenv("BITGET_PASSPHRASE"))
    })

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)

    if not data:
        print("IGNORED EMPTY PAYLOAD", flush=True)
        return jsonify({"ignored": True}), 200

    action = data.get("action")
    symbol = data.get("symbol")

    print(
        f"[{datetime.now()}] ACTION={action} SYMBOL={symbol}",
        flush=True
    )

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
