"""
CodeCraftHub - Personalized Learning Platform (Backend API)

A simple Flask REST API that manages course listings with full CRUD.
Data is stored in a local JSON file (courses.json) - no database needed.

Run:
    pip install -r requirements.txt
    python app.py
The API listens on http://localhost:5000
"""

import json
import os
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# CORS: lets the browser-based dashboard (Part 2) call this API.
# Uses Flask-CORS when installed; otherwise adds the same headers manually.
# ---------------------------------------------------------------------------
try:
    from flask_cors import CORS

    CORS(app, resources={r"/api/*": {"origins": "*"}})
except ImportError:  # pragma: no cover - fallback when flask-cors is missing
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json")
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]
REQUIRED_FIELDS = ["name", "description", "target_date", "status"]
DATE_FORMAT = "%Y-%m-%d"

_file_lock = threading.Lock()


# ---------------------------------------------------------------------------
# JSON file storage helpers
# ---------------------------------------------------------------------------
def load_courses():
    """Read all courses from the JSON file. Creates the file if missing."""
    if not os.path.exists(DATA_FILE):
        save_courses([])
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            data = json.loads(content) if content else []
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Could not read data file: {exc}") from exc


def save_courses(courses):
    """Write all courses back to the JSON file (atomic write)."""
    tmp_path = DATA_FILE + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(courses, f, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except OSError as exc:
        raise RuntimeError(f"Could not write data file: {exc}") from exc


def next_id(courses):
    """Auto-increment ID starting at 1."""
    return max((c["id"] for c in courses), default=0) + 1


def find_course(courses, course_id):
    return next((c for c in courses if c["id"] == course_id), None)


# ---------------------------------------------------------------------------
# Response helpers (consistent JSON shape)
# ---------------------------------------------------------------------------
def success(data=None, message=None, status_code=200):
    body = {"success": True}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def error(message, status_code=400, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status_code


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_course(payload, partial=False):
    """Return a list of validation error messages (empty list = valid).

    partial=True is used for PUT so clients may send only changed fields.
    """
    errors = []

    if not isinstance(payload, dict):
        return ["Request body must be a JSON object."]

    if not partial:
        missing = [f for f in REQUIRED_FIELDS if f not in payload]
        if missing:
            errors.append(f"Missing required field(s): {', '.join(missing)}.")

    for field in ("name", "description"):
        if field in payload:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"'{field}' must be a non-empty string.")

    if "target_date" in payload:
        value = payload["target_date"]
        try:
            datetime.strptime(str(value), DATE_FORMAT)
        except ValueError:
            errors.append("'target_date' must be a valid date in YYYY-MM-DD format.")

    if "status" in payload and payload["status"] not in VALID_STATUSES:
        errors.append(f"'status' must be one of: {', '.join(VALID_STATUSES)}.")

    unknown = [k for k in payload if k not in REQUIRED_FIELDS and k not in ("id", "created_at")]
    if unknown:
        errors.append(f"Unknown field(s): {', '.join(unknown)}.")

    return errors


def get_json_body():
    """Parse the JSON body, returning (data, error_response)."""
    if not request.is_json:
        return None, error("Content-Type must be application/json.", 415)
    data = request.get_json(silent=True)
    if data is None:
        return None, error("Request body is not valid JSON.", 400)
    return data, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return success(
        {
            "name": "CodeCraftHub API",
            "endpoints": [
                "GET    /api/courses",
                "GET    /api/courses/<id>",
                "POST   /api/courses",
                "PUT    /api/courses/<id>",
                "DELETE /api/courses/<id>",
                "GET    /api/courses/stats",
            ],
        },
        "Welcome to CodeCraftHub!",
    )


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """List all courses. Optional filters: ?status=...  ?search=..."""
    courses = load_courses()

    status = request.args.get("status")
    if status:
        if status not in VALID_STATUSES:
            return error(f"'status' filter must be one of: {', '.join(VALID_STATUSES)}.")
        courses = [c for c in courses if c["status"] == status]

    search = request.args.get("search", "").strip().lower()
    if search:
        courses = [
            c for c in courses
            if search in c["name"].lower() or search in c["description"].lower()
        ]

    return success(courses)


@app.route("/api/courses/stats", methods=["GET"])
def get_stats():
    """Optional exploration: totals per status."""
    courses = load_courses()
    by_status = {s: 0 for s in VALID_STATUSES}
    for c in courses:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    return success({"total": len(courses), "by_status": by_status})


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    course = find_course(load_courses(), course_id)
    if not course:
        return error(f"Course with id {course_id} not found.", 404)
    return success(course)


@app.route("/api/courses", methods=["POST"])
def create_course():
    payload, err = get_json_body()
    if err:
        return err

    errors = validate_course(payload)
    if errors:
        return error("Validation failed.", 400, errors)

    with _file_lock:
        courses = load_courses()
        course = {
            "id": next_id(courses),
            "name": payload["name"].strip(),
            "description": payload["description"].strip(),
            "target_date": payload["target_date"],
            "status": payload["status"],
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        courses.append(course)
        save_courses(courses)

    return success(course, "Course created successfully.", 201)


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    payload, err = get_json_body()
    if err:
        return err

    errors = validate_course(payload, partial=True)
    if errors:
        return error("Validation failed.", 400, errors)

    with _file_lock:
        courses = load_courses()
        course = find_course(courses, course_id)
        if not course:
            return error(f"Course with id {course_id} not found.", 404)

        for field in REQUIRED_FIELDS:
            if field in payload:
                value = payload[field]
                course[field] = value.strip() if isinstance(value, str) else value
        save_courses(courses)

    return success(course, "Course updated successfully.")


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    with _file_lock:
        courses = load_courses()
        course = find_course(courses, course_id)
        if not course:
            return error(f"Course with id {course_id} not found.", 404)
        courses.remove(course)
        save_courses(courses)

    return success(course, f"Course {course_id} deleted successfully.")


# ---------------------------------------------------------------------------
# Error handlers (keep every response JSON)
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(_e):
    return error("Resource not found.", 404)


@app.errorhandler(405)
def method_not_allowed(_e):
    return error("Method not allowed on this endpoint.", 405)


@app.errorhandler(500)
def server_error(_e):
    return error("Internal server error.", 500)


@app.errorhandler(RuntimeError)
def storage_error(e):
    return error(str(e), 500)


if __name__ == "__main__":
    load_courses()  # make sure courses.json exists
    print("- CodeCraftHub API is starting...")
    print(f"- Data will be stored in: {DATA_FILE}")
    print("- API will be available at: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
