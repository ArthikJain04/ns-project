import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from scanner import WebScanner
from database import db, UserScan
from aws_s3 import upload_report_to_s3

# Load environment variables (AWS keys, DB URI) from .env file
load_dotenv()

app = Flask(__name__)
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
    
    # Append the S3 URL to the results to be seen in frontend (if desired)
    if s3_report_url:
        results['s3_report'] = s3_report_url
        
    return jsonify(results)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Endpoint to fetch scan history from the database."""
    scans = UserScan.query.order_by(UserScan.timestamp.desc()).all()
    return jsonify([scan.to_dict() for scan in scans])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
