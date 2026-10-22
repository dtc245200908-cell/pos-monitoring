from flask import Flask, jsonify, request, render_template, redirect
from database import init_db, get_connection
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
init_db()

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
    with get_connection() as conn:
        apartments = conn.execute(
            "SELECT * FROM apartments ORDER BY id DESC"
        ).fetchall()

    total = len(apartments)
    occupied = sum(
        1 for apartment in apartments
        if apartment["status"] == "Đang sử dụng"
    )
    available = total - occupied

    return render_template(
        "index.html",
        apartments=apartments,
        total=total,
        occupied=occupied,
        available=available
    )

@app.route("/residents")
def residents_page():
    with get_connection() as conn:
        residents = conn.execute("""
            SELECT residents.id,
                   residents.full_name,
                   residents.phone,
                   apartments.code AS apartment_code
            FROM residents
with get_connection() as conn:
    apartments = conn.execute(
        "SELECT * FROM apartments ORDER BY id DESC"
    ).fetchall()with get_connection() as conn:
    apartments = conn.execute(
        "SELECT * FROM apartments ORDER BY id DESC"
    ).fetchall()with get_connection() as conn:
    apartments = conn.execute(
        "SELECT * FROM apartments ORDER BY id DESC"
    ).fetchall()            JOIN apartments
              ON residents.apartment_id = apartments.id
            ORDER BY residents.id DESC
        """).fetchall()

        apartments = conn.execute(
            "SELECT id, code FROM apartments ORDER BY code"
        ).fetchall()

    return render_template(
        "residents.html",
        residents=residents,
        apartments=apartments
    )



@app.route("/residents/add", methods=["POST"])
def add_resident():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    apartment_text = request.form.get("apartment_id", "").strip()

    if not full_name or not phone or not apartment_text:
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400

    if not phone.isdigit() or not (9 <= len(phone) <= 11):
        return jsonify({"error": "Số điện thoại không hợp lệ"}), 400

    try:
        apartment_id = int(apartment_text)
    except ValueError:
        return jsonify({"error": "Căn hộ không hợp lệ"}), 400

    with get_connection() as conn:
        apartment = conn.execute(
            "SELECT id FROM apartments WHERE id = ?",
            (apartment_id,)
        ).fetchone()

        if apartment is None:
            return jsonify({"error": "Không tìm thấy căn hộ"}), 404

        conn.execute(
            """INSERT INTO residents (full_name, phone, apartment_id)
               VALUES (?, ?, ?)""",
            (full_name, phone, apartment_id)
        )
        conn.commit()

    return redirect("/residents")

@app.route("/residents/<int:resident_id>/edit", methods=["GET", "POST"])
def edit_resident(resident_id):
    with get_connection() as conn:
        resident = conn.execute(
            "SELECT * FROM residents WHERE id = ?",
            (resident_id,)
        ).fetchone()

        if resident is None:
            return "Không tìm thấy cư dân", 404

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            phone = request.form.get("phone", "").strip()
            apartment_text = request.form.get("apartment_id", "").strip()

            if not full_name or not phone or not apartment_text:
                return "Vui lòng nhập đầy đủ thông tin", 400

            if not phone.isdigit() or not (9 <= len(phone) <= 11):
                return "Số điện thoại không hợp lệ", 400

            try:
                apartment_id = int(apartment_text)
            except ValueError:
                return "Căn hộ không hợp lệ", 400

            apartment = conn.execute(
                "SELECT id FROM apartments WHERE id = ?",
                (apartment_id,)
            ).fetchone()

            if apartment is None:
                return "Không tìm thấy căn hộ", 404

            conn.execute(
                """UPDATE residents
                   SET full_name = ?, phone = ?, apartment_id = ?
                   WHERE id = ?""",
                (full_name, phone, apartment_id, resident_id)
            )
            conn.commit()

            return redirect("/residents")

        apartments = conn.execute(
            "SELECT id, code FROM apartments ORDER BY code"
        ).fetchall()

    return render_template(
        "edit_resident.html",
        resident=resident,
        apartments=apartments
    )

@app.route("/residents/<int:resident_id>/delete", methods=["POST"])
def delete_resident(resident_id):
    with get_connection() as conn:
        resident = conn.execute(
            "SELECT id FROM residents WHERE id = ?",
            (resident_id,)
        ).fetchone()

        if resident is None:
            return "Không tìm thấy cư dân", 404

        conn.execute(
            "DELETE FROM residents WHERE id = ?",
            (resident_id,)
        )
        conn.commit()

    return redirect("/residents")








@app.route("/products")
def get_products():
    return jsonify(products)


@app.route("/apartments/add", methods=["POST"])
def add_apartment():
    import sqlite3

    code = request.form.get("code", "").strip().upper()
    floor_text = request.form.get("floor", "").strip()
    area_text = request.form.get("area", "").strip()
    status = request.form.get("status", "Còn trống")

    if not code or not floor_text or not area_text:
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400

    try:
        floor = int(floor_text)
        area = float(area_text)
    except ValueError:
        return jsonify({"error": "Tầng hoặc diện tích không hợp lệ"}), 400

    if floor < 1 or area <= 0:
        return jsonify({"error": "Tầng và diện tích phải lớn hơn 0"}), 400

    if status not in ("Còn trống", "Đang sử dụng"):
        return jsonify({"error": "Trạng thái không hợp lệ"}), 400

    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO apartments (code, floor, area, status)
                   VALUES (?, ?, ?, ?)""",
                (code, floor, area, status)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Mã căn hộ đã tồn tại"}), 409

    return redirect("/")

@app.route("/apartments/<int:apartment_id>/edit", methods=["GET", "POST"])
def edit_apartment(apartment_id):
    
    if request.method == "GET":
        with get_connection() as conn:
            apartment = conn.execute(
                "SELECT * FROM apartments WHERE id = ?",
                (apartment_id,)
            ).fetchone()

        if apartment is None:
            return jsonify({"error": "Không tìm thấy căn hộ"}), 404

        return render_template("edit_apartment.html", apartment=apartment)
    import sqlite3

    code = request.form.get("code", "").strip().upper()
    floor_text = request.form.get("floor", "").strip()
    area_text = request.form.get("area", "").strip()
    status = request.form.get("status", "").strip()

    if not code or not floor_text or not area_text:
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400

    try:
        floor = int(floor_text)
        area = float(area_text)
    except ValueError:
        return jsonify({"error": "Tầng hoặc diện tích không hợp lệ"}), 400

    if floor < 1 or not (0 < area < float("inf")):
        return jsonify({"error": "Tầng hoặc diện tích không hợp lệ"}), 400

    if status not in ("Còn trống", "Đang sử dụng"):
        return jsonify({"error": "Trạng thái không hợp lệ"}), 400

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """UPDATE apartments
                   SET code = ?, floor = ?, area = ?, status = ?
                   WHERE id = ?""",
                (code, floor, area, status, apartment_id)
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Không tìm thấy căn hộ"}), 404
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Mã căn hộ đã tồn tại"}), 409

    return redirect("/")



@app.route("/apartments/<int:apartment_id>/delete", methods=["POST"])
def delete_apartment(apartment_id):
    with get_connection() as conn:
        apartment = conn.execute(
            "SELECT * FROM apartments WHERE id = ?",
            (apartment_id,)
        ).fetchone()

        if apartment is None:
            return jsonify({"error": "Không tìm thấy căn hộ"}), 404

        if apartment["status"] == "Đang sử dụng":
            return jsonify({
                "error": "Không thể xóa căn hộ đang sử dụng"
            }), 400

        conn.execute(
            "DELETE FROM apartments WHERE id = ?",
            (apartment_id,)
        )
        conn.commit()

    return redirect("/")



@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

