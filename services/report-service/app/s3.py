import os

import boto3
from botocore.config import Config


AWS_REGION = os.getenv("AWS_REGION")

if not AWS_REGION:
    raise RuntimeError("AWS_REGION environment variable is required")


BUCKET_NAME = os.getenv("S3_BUCKET")

if not BUCKET_NAME:
    raise RuntimeError("S3_BUCKET environment variable is required")


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(
        signature_version="s3v4"
    ),
)