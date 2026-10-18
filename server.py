from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "MONSTER V4 ONLINE"

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json(force=True)

    print("Recebido:", data)

    return jsonify({
        "success": True,
        "data": data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
