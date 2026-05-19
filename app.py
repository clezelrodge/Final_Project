from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from functools import wraps
import os
import socket
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "filetrack_secret_key_2026")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ================= DATABASE CONNECTION =================

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "filetrackdb"),
            port=int(os.getenv("DB_PORT", "3306")),
            autocommit=True
        )
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        return None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


# ================= HARDWARE STATUS =================

HARDWARE_STATUS = {
    "esp32": "Offline",
    "rfid_reader": "Inactive",
    "lcd_display": "Waiting",
    "buzzer": "OFF",
    "led_status": "OFF",
    "selected_action": "None",
    "last_rfid": "None",
    "last_document": "None",
    "last_event": "No activity",
    "last_updated": "Never"
}


def update_hardware_status(**kwargs):
    for key, value in kwargs.items():
        if value is not None:
            HARDWARE_STATUS[key] = value

    HARDWARE_STATUS["last_updated"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")


# ================= AUTH DECORATORS =================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Admin access required", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ================= MAIN ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        selected_role = request.form.get("role", request.args.get("role", "user"))

        db = get_db_connection()
        if not db:
            flash("Database connection failed", "error")
            return render_template("login.html")

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            if user["role"] != selected_role:
                flash("Invalid role selected.", "error")
                return render_template("login.html")

            password_valid = False

            try:
                password_valid = check_password_hash(user["password"], password)
            except:
                password_valid = False

            if user["password"] == password:
                password_valid = True

            if password_valid:
                if selected_role == "admin":
                    admin_pin = request.form.get("admin_pin", "")
                    if admin_pin and admin_pin != os.getenv("ADMIN_PIN", "1234"):
                        flash("Invalid Admin PIN", "error")
                        return render_template("login.html")

                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["full_name"] = user["full_name"]
                session["role"] = user["role"]

                if user["role"] == "admin":
                    return redirect(url_for("admin_dashboard"))
                return redirect(url_for("user_dashboard"))

        flash("Invalid username or password", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ================= ADMIN ROUTES =================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return render_template(
            "admin/admin_dashboard.html",
            total_documents=0,
            storage_slots=0,
            active_users=0,
            retrieval_logs=0,
            documents=[],
            logs=[]
        )

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS count FROM Documents")
    total_documents = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM Columns")
    storage_slots = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM Users WHERE role = 'user'")
    active_users = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM AccessLogs")
    retrieval_logs = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT('Column ', c.column_label) AS location
        FROM Documents d
        LEFT JOIN Columns c ON d.column_id = c.column_id
        ORDER BY d.updated_at DESC
        LIMIT 10
    """)
    documents = cursor.fetchall()

    cursor.execute("""
        SELECT a.log_id, d.title, d.rfid_tag, d.status,
               u.full_name AS requested_by,
               a.action,
               DATE_FORMAT(a.action_timestamp, '%Y-%m-%d %h:%i %p') AS formatted_time
        FROM AccessLogs a
        JOIN Documents d ON a.doc_id = d.doc_id
        JOIN Users u ON a.requested_by_user_id = u.user_id
        ORDER BY a.action_timestamp DESC
        LIMIT 10
    """)
    logs = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_documents=total_documents,
        storage_slots=storage_slots,
        active_users=active_users,
        retrieval_logs=retrieval_logs,
        documents=documents,
        logs=logs,
        hardware_status=HARDWARE_STATUS
    )


@app.route("/admin/documents")
@admin_required
def admin_documents():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return redirect(url_for("admin_dashboard"))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.*, CONCAT('Column ', c.column_label) AS location
        FROM Documents d
        LEFT JOIN Columns c ON d.column_id = c.column_id
        ORDER BY d.updated_at DESC
    """)
    documents = cursor.fetchall()

    cursor.execute("SELECT * FROM Users WHERE role = 'user'")
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/admin_documents.html", documents=documents, users=users)


@app.route("/admin/storage")
@admin_required
def admin_storage():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return redirect(url_for("admin_dashboard"))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.column_id, c.column_label,
               COUNT(d.doc_id) AS total_documents,
               SUM(CASE WHEN d.status = 'Available' THEN 1 ELSE 0 END) AS available_count,
               SUM(CASE WHEN d.status = 'Borrowed' THEN 1 ELSE 0 END) AS borrowed_count
        FROM Columns c
        LEFT JOIN Documents d ON d.column_id = c.column_id
        GROUP BY c.column_id, c.column_label
        ORDER BY c.column_label
    """)
    columns = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/admin_storage.html", columns=columns)


@app.route("/admin/users")
@admin_required
def admin_users():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return redirect(url_for("admin_dashboard"))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, full_name, email, role, created_at FROM Users ORDER BY created_at DESC")
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/admin_users.html", users=users)


@app.route("/admin/logs")
@admin_required
def admin_logs():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return redirect(url_for("admin_dashboard"))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.log_id, d.title, d.rfid_tag, a.action,
               u.full_name AS requested_by,
               DATE_FORMAT(a.action_timestamp, '%Y-%m-%d %h:%i %p') AS formatted_time
        FROM AccessLogs a
        JOIN Documents d ON a.doc_id = d.doc_id
        JOIN Users u ON a.requested_by_user_id = u.user_id
        ORDER BY a.action_timestamp DESC
        LIMIT 100
    """)
    logs = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/admin_logs.html", logs=logs)


@app.route("/admin/hardware")
@admin_required
def admin_hardware():
    return render_template("admin/admin_hardware.html", hardware_status=HARDWARE_STATUS)


# ================= USER ROUTES =================

@app.route("/user/dashboard")
@login_required
def user_dashboard():
    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return render_template("user/user_dashboard.html", documents=[])

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT('Column ', c.column_label) AS location
        FROM Documents d
        LEFT JOIN Columns c ON d.column_id = c.column_id
        ORDER BY d.updated_at DESC
    """)
    documents = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("user/user_dashboard.html", documents=documents)


@app.route("/user/records")
@login_required
def user_records():
    return redirect(url_for("user_dashboard"))


@app.route("/user/requests")
@login_required
def user_requests():
    return redirect(url_for("user_dashboard"))


# ================= DOCUMENT FUNCTIONS =================

@app.route("/admin/add_document", methods=["POST"])
@admin_required
def add_document():
    title = request.form.get("title", "").strip()
    rfid_tag = request.form.get("rfid_tag", "").strip()
    column_id = request.form.get("column_id")
    status = "Available"

    db = get_db_connection()
    if not db:
        flash("Database connection failed", "error")
        return redirect(url_for("admin_documents"))

    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO Documents (title, rfid_tag, column_id, status)
            VALUES (%s, %s, %s, %s)
        """, (title, rfid_tag, column_id, status))

        flash("Document added successfully!", "success")

    except mysql.connector.Error as err:
        flash(f"Error adding document: {err}", "error")

    cursor.close()
    db.close()

    return redirect(url_for("admin_documents"))


@app.route("/search")
@login_required
def search():
    query = request.args.get("q", "")

    db = get_db_connection()
    if not db:
        return jsonify([])

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.doc_id, d.title, d.rfid_tag, d.status,
               CONCAT('Column ', c.column_label) AS location
        FROM Documents d
        LEFT JOIN Columns c ON d.column_id = c.column_id
        WHERE d.title LIKE %s OR d.rfid_tag LIKE %s
        ORDER BY d.title
    """, (f"%{query}%", f"%{query}%"))

    documents = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(documents)


# ================= RFID / HARDWARE INTEGRATION =================

def process_rfid_scan(rfid_tag, action_type):
    action_type = (action_type or "search").lower()

    db = get_db_connection()
    if not db:
        update_hardware_status(
            esp32="Connected",
            rfid_reader="Scanned",
            lcd_display="Database Error",
            buzzer="ON",
            led_status="Red",
            selected_action=action_type,
            last_rfid=rfid_tag,
            last_event="Database connection failed"
        )
        return {"success": False, "message": "Database connection failed", "status": HARDWARE_STATUS}, 500

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Documents WHERE rfid_tag = %s", (rfid_tag,))
    document = cursor.fetchone()

    if not document:
        update_hardware_status(
            esp32="Connected",
            rfid_reader="Scanned",
            lcd_display="RFID Not Found",
            buzzer="ON",
            led_status="Red",
            selected_action=action_type,
            last_rfid=rfid_tag,
            last_document="Unknown",
            last_event="RFID tag not found"
        )

        cursor.close()
        db.close()

        return {"success": False, "message": "RFID tag not found", "status": HARDWARE_STATUS}, 404

    cursor.execute("SELECT user_id FROM Users WHERE role='user' ORDER BY user_id LIMIT 1")
    user = cursor.fetchone()

    cursor.execute("SELECT user_id FROM Users WHERE role='admin' ORDER BY user_id LIMIT 1")
    admin = cursor.fetchone()

    user_id = user["user_id"] if user else 1
    admin_id = admin["user_id"] if admin else 1

    message = "Document located"
    new_status = document["status"]
    log_action = "Search"
    led = "Green"

    if action_type == "borrow":
        log_action = "Check Out"
        if document["status"] == "Available":
            new_status = "Borrowed"
            message = "BORROW SUCCESS"
            led = "Yellow"
        else:
            message = "Document is not available"
            led = "Red"
            update_hardware_status(
                esp32="Connected",
                rfid_reader="Scanned",
                lcd_display=message,
                buzzer="ON",
                led_status=led,
                selected_action=action_type,
                last_rfid=rfid_tag,
                last_document=document["title"],
                last_event=message
            )
            cursor.close()
            db.close()
            return {"success": False, "message": message, "status": HARDWARE_STATUS}, 409

    elif action_type == "return":
        log_action = "Return"
        if document["status"] == "Borrowed":
            new_status = "Available"
            message = "RETURN SUCCESS"
            led = "Green"
        else:
            message = "Document already available"
            led = "Green"

    elif action_type == "search":
        message = "DOCUMENT FOUND"
        led = "Green"

    if new_status != document["status"]:
        cursor.execute(
            "UPDATE Documents SET status=%s, updated_at=CURRENT_TIMESTAMP WHERE doc_id=%s",
            (new_status, document["doc_id"])
        )

    cursor.execute("""
        INSERT INTO AccessLogs (doc_id, requested_by_user_id, processed_by_admin_id, action)
        VALUES (%s, %s, %s, %s)
    """, (document["doc_id"], user_id, admin_id, log_action))

    update_hardware_status(
        esp32="Connected",
        rfid_reader="Scanned",
        lcd_display=message,
        buzzer="ON",
        led_status=led,
        selected_action=action_type,
        last_rfid=rfid_tag,
        last_document=document["title"],
        last_event=message
    )

    cursor.close()
    db.close()

    return {
        "success": True,
        "message": message,
        "title": document["title"],
        "status": new_status,
        "hardware_status": HARDWARE_STATUS
    }, 200


@app.route("/api/hardware/scan", methods=["POST"])
def hardware_scan():
    data = request.get_json(silent=True) or {}

    rfid_tag = (
        data.get("rfid_tag") or
        data.get("rfid") or
        data.get("tag") or
        ""
    ).strip()

    action_type = data.get("action") or data.get("button") or "search"

    payload, status_code = process_rfid_scan(rfid_tag, action_type)

    return jsonify(payload), status_code


@app.route("/api/hardware/status")
def hardware_status():
    return jsonify(HARDWARE_STATUS)


@app.route("/simulate_scan", methods=["POST"])
@login_required
def simulate_scan():
    rfid_tag = request.form.get("rfid_tag", "").strip()
    action_type = request.form.get("action", "search").strip()

    payload, status_code = process_rfid_scan(rfid_tag, action_type)

    flash(payload["message"], "success" if status_code == 200 else "error")

    return redirect(url_for("admin_dashboard"))


# ================= ERROR HANDLERS =================

@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("index.html"), 500


# ================= RUN SERVER =================

if __name__ == "__main__":
    ip = get_local_ip()
    port = int(os.getenv("FILETRACK_PORT", "5000"))

    print("Starting FileTrack Web Server...")
    print(f"Website: http://127.0.0.1:{port}")
    print(f"ESP32 API: http://{ip}:{port}/api/hardware/scan")

    app.run(
        host="0.0.0.0",
        debug=True,
        port=port,
        use_reloader=False
    )