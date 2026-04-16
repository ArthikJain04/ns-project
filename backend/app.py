import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from asgiref.wsgi import WsgiToAsgi

from scanner import WebScanner
from database import db, UserScan
from aws_s3 import upload_report_to_s3

# Load environment variables (AWS keys, DB URI) from .env file
load_dotenv()

# Path to the React build output (frontend/dist)
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

app = Flask(__name__, static_folder=DIST_DIR, static_url_path='')
CORS(app)

# Configure AWS RDS Database (or local SQLite fallback if not configured)
db_url = os.environ.get('DATABASE_URL')
if not db_url or db_url.strip() == "":
    db_url = 'sqlite:///local_scans.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# ── API Routes ──────────────────────────────────────────────────────────────

@app.route('/api/scan', methods=['POST'])
def run_scan():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # 1. Run the Python Web Scanner Engine
    scanner = WebScanner(target_url)
    results = scanner.run_full_scan()

    # 2. Upload the JSON Report to Amazon S3
    s3_report_url = upload_report_to_s3(results)

    # 3. Save the scan entry to Amazon RDS (Database)
    try:
        new_scan = UserScan(
            target_url=target_url,
            s3_report_url=s3_report_url
        )
        db.session.add(new_scan)
        db.session.commit()
    except Exception as e:
        print(f"Failed to save to database: {e}")
        db.session.rollback()

    if s3_report_url:
        results['s3_report'] = s3_report_url

    return jsonify(results)


@app.route('/api/history', methods=['GET'])
def get_history():
    """Endpoint to fetch scan history from the database."""
    scans = UserScan.query.order_by(UserScan.timestamp.desc()).all()
    return jsonify([scan.to_dict() for scan in scans])


# ── Serve React Frontend (dist/) ──────────────────────────────────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React SPA from the built dist/ folder."""
    file_path = os.path.join(DIST_DIR, path)
    if path != '' and os.path.exists(file_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


# ── ASGI wrapper for Uvicorn ──────────────────────────────────────────────
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:asgi_app", host="0.0.0.0", port=5000, reload=True)
