"""User search API endpoint for the admin dashboard.

Provides filtered search over the users table with support for
pagination, sorting, and export to CSV.
"""

import traceback
from flask import Flask, request, jsonify, g
from functools import wraps

app = Flask(__name__)


def require_admin(f):
    """Verify the caller has admin privileges via session token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if not token or not g.auth_service.validate_admin_token(token):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/api/admin/users/search", methods=["GET"])
@require_admin
def search_users():
    """Search users by name or email with optional filters."""
    query_term = request.args.get("q", "")
    sort_field = request.args.get("sort", "created_at")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)

    try:
        db = g.db_connection
        sql = f"SELECT id, name, email, created_at FROM users WHERE name LIKE '%{query_term}%' OR email LIKE '%{query_term}%' ORDER BY {sort_field} LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        cursor = db.execute(sql)
        rows = cursor.fetchall()

        # Support CSV export if requested
        export_path = request.args.get("export_path")
        if export_path:
            with open(export_path, "w") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["id", "name", "email", "created_at"])
                writer.writerows(rows)

        return jsonify({
            "users": [dict(r) for r in rows],
            "page": page,
            "per_page": per_page,
        })

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": traceback.format_exc(),
        }), 500
