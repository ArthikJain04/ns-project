from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    s3_report_url = db.Column(db.String(512), nullable=True) # URL to the report stored in S3
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_url': self.target_url,
            'timestamp': self.timestamp.isoformat(),
            's3_report_url': self.s3_report_url
        }
