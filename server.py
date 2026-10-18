from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "MONSTER V4 ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    action = data.get("action")
    symbol = data.get("symbol")

    print(f"ACTION={action}")
    print(f"SYMBOL={symbol}")

    return jsonify({
        "success": True,
        "action": action,
        "symbol": symbol
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
