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
        "payment_status": "Payment processing fixed"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "version": VERSION
    }), 200

@app.route("/products")
def products():
    return jsonify({
        "products": [
            {"id": 1, "name": "Laptop", "price": 55000},
            {"id": 2, "name": "Mobile", "price": 25000},
            {"id": 3, "name": "Headphones", "price": 3000}
        ]
    })

@app.route("/product/<int:product_id>")
def product_details(product_id):
    return jsonify({
        "product_id": product_id,
        "name": "Laptop",
        "price": 55000,
        "category": "Electronics",
        "availability": "In Stock"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)