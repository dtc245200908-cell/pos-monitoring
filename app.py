from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "pos_http_requests_total",
    "Total POS HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "pos_http_request_duration_seconds",
    "POS HTTP request duration",
    ["endpoint"]
)

products = [
    {"id": 1, "name": "Sua tuoi", "price": 10000},
    {"id": 2, "name": "Banh mi", "price": 15000},
    {"id": 3, "name": "Nuoc suoi", "price": 5000}
]

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        endpoint = request.url_rule.rule if request.url_rule else "unknown"
        REQUEST_COUNT.labels(
            request.method, endpoint, str(response.status_code)
        ).inc()
        REQUEST_LATENCY.labels(endpoint).observe(
            time.perf_counter() - request.start_time
        )
    return response

@app.route("/")
def home():
    return jsonify({"message": "POS System is running"})

@app.route("/products")
def get_products():
    return jsonify(products)

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
