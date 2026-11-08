from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():

    try:
        data = request.json

        action = data.get("action")
        symbol = data.get("symbol")
        price = data.get("price")
        timestamp = data.get("timestamp")

        print(
            f"[{datetime.utcnow()}] "
            f"ACTION={action} "
            f"SYMBOL={symbol} "
            f"PRICE={price} "
            f"TIME={timestamp}"
        )

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print(str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
