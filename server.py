from flask import Flask
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():

    return {
        "api_key": bool(os.getenv("BITGET_API_KEY")),
        "secret": bool(os.getenv("BITGET_API_SECRET")),
        "passphrase": bool(os.getenv("BITGET_PASSPHRASE"))
    }

@app.route("/bitget-test")
def bitget_test():

    return {
        "status": "api_loaded",
        "api_key": os.getenv("BITGET_API_KEY")[:8] + "..."
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
