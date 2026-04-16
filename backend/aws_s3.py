import boto3
import json
import os
import uuid
from datetime import datetime

def upload_report_to_s3(report_data):
    """
    Uploads a vulnerability report dictionary as a JSON file to AWS S3.
    Requires AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_S3_BUCKET_NAME in environment.
    """
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not bucket_name or not access_key or not secret_key:
        print("AWS S3 Credentials or Bucket Name missing. Skipping S3 upload.")
        return None
        
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Create a unique filename for the report
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        target_domain = report_data.get('target', 'unknown_target').replace('http://', '').replace('https://', '').split('/')[0]
        filename = f"reports/{target_domain}_{timestamp_str}_{uuid.uuid4().hex[:6]}.json"
        
        # Convert dictionary to JSON string
        json_content = json.dumps(report_data, indent=4)
        
        # Upload object
        s3.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=json_content,
            ContentType='application/json'
        )
        
        # Generate the S3 URL (assuming it's private, but returning the standard S3 URI format or an https link)
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        print(f"Successfully uploaded scan report to S3: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f"Failed to upload to S3: {str(e)}")
        return None
