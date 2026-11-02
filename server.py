from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/uta-test")
def uta_test():

    path = "/api/v3/position/current-position"

    params = "?category=USDT-FUTURES"

    timestamp = str(int(time.time() * 1000))

    sign_message = timestamp + "GET" + path + params

    signature = base64.b64encode(
        hmac.new(
            API_SECRET.encode(),
            sign_message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.get(
        BASE_URL + path + params,
        headers=headers,
        timeout=20
    )

    return jsonify(response.json())
