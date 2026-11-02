from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)

    if not data:
        print("IGNORED EMPTY PAYLOAD", flush=True)
        return jsonify({"ignored": True}), 200

    action = data.get("action")
    symbol = data.get("symbol")

    if not action or not symbol:
        print(f"INVALID PAYLOAD: {data}", flush=True)
        return jsonify({"ignored": True}), 200

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol}",
        flush=True
    )

    return jsonify({"success": True})
