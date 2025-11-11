import boto3
import os
from dotenv import load_dotenv
load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
bucket_name = os.getenv("AWS_BUCKET_NAME")

try:
    with open("image.jpeg", "rb") as f:
        file_data = f.read()

    s3_client.put_object(
        Bucket=bucket_name,
        Key="image.jpeg",
        Body=file_data,
    )
    print("S3 upload succeeded!")
except Exception as e:
    print("S3 upload failed:", e)
