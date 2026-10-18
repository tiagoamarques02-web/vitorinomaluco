from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():

    api = os.getenv("BITGET_API_KEY")
    secret = os.getenv("BITGET_API_SECRET")
    passphrase = os.getenv("BITGET_PASSPHRASE")

    return {
        "api_key": api is not None,
        "secret": secret is not None,
        "passphrase": passphrase is not None
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
