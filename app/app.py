from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "4.2.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "UAT")

@app.route("/")
def home():
    return jsonify({
        "application": "Retail Platform",
        "version": VERSION,
        "environment": ENVIRONMENT,
        "payment_status": "Payment processing available"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "version": VERSION
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)