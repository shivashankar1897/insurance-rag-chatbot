import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from src.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET,
)


def get_s3_client():
    """
    Create and return an S3 client.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def file_exists(s3_key: str) -> bool:
    """
    Check whether an object exists in S3.
    """
    client = get_s3_client()

    try:
        client.head_object(Bucket=S3_BUCKET, Key=s3_key)
        return True
    except ClientError:
        return False


def list_files(prefix: str = ""):
    """
    List all files under an S3 prefix.
    """
    client = get_s3_client()

    paginator = client.get_paginator("list_objects_v2")

    files = []

    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):

        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            files.append(obj["Key"])

    return files


def download_folder(prefix: str, local_folder: str):
    """
    Download an S3 folder recursively.
    """
    client = get_s3_client()

    Path(local_folder).mkdir(parents=True, exist_ok=True)

    paginator = client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):

        if "Contents" not in page:
            continue

        for obj in page["Contents"]:

            key = obj["Key"]

            if key.endswith("/"):
                continue

            relative_path = key[len(prefix):]

            local_path = os.path.join(local_folder, relative_path)

            Path(local_path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            client.download_file(
                S3_BUCKET,
                key,
                local_path,
            )

            print(f"Downloaded: {key}")


def upload_file(local_path: str, s3_key: str):
    """
    Upload a single file to S3.
    """
    client = get_s3_client()

    client.upload_file(
        local_path,
        S3_BUCKET,
        s3_key,
    )

    print(f"Uploaded: {s3_key}")


def upload_folder(local_folder: str, s3_prefix: str):
    """
    Upload an entire folder recursively.
    """
    for root, _, files in os.walk(local_folder):

        for file in files:

            local_path = os.path.join(root, file)

            relative_path = os.path.relpath(
                local_path,
                local_folder,
            )

            s3_key = f"{s3_prefix}/{relative_path}".replace("\\", "/")

            upload_file(local_path, s3_key)