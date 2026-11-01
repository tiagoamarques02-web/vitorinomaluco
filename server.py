@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True)

    print("RAW:", data, flush=True)

    if not data:
        return jsonify({"ignored": True}), 200

    action = data.get("action")
    symbol = data.get("symbol")

    print(
        f"[{datetime.now()}] "
        f"ACTION={action} "
        f"SYMBOL={symbol}",
        flush=True
    )

    return jsonify({"success": True})
