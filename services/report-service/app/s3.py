# report-service/app/s3.py
import boto3
import os
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET_NAME = os.getenv("S3_BUCKET", "ai-health-reports")

# boto3 resolves credentials from the environment, the local AWS profile, or
# EKS Pod Identity. Do not require static keys during module import.
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(signature_version="s3v4"),
)