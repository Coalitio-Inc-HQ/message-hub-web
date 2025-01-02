import boto3
from core.config_reader import config

s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.S3_ACCESS_KEY_ID,
    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
    # region_name=settings.aws_region,
    endpoint_url=config.S3_BUCKET_URL
)