"""
Storage module for RCKG.

Provides MinIO/S3-compatible object storage client for regulatory documents,
markdown conversions, and evidence artifacts.
"""

import os
from typing import Optional, BinaryIO
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


class MinIOStorage:
    """
    MinIO/S3-compatible object storage client.

    This client provides a unified interface for storing and retrieving
    regulatory documents, markdown conversions, and evidence artifacts.

    Configuration via environment variables:
        - MINIO_ENDPOINT_URL: MinIO server URL (default: http://localhost:9000)
        - MINIO_ACCESS_KEY: Access key (default: rckg_admin)
        - MINIO_SECRET_KEY: Secret key (default: rckg_secret_password)
        - MINIO_REGION: AWS region (default: us-east-1)
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize MinIO storage client.

        Args:
            endpoint_url: MinIO server endpoint URL
            access_key: Access key for authentication
            secret_key: Secret key for authentication
            region: AWS region (for bucket location configuration)
        """
        self.endpoint_url = endpoint_url or os.getenv(
            "MINIO_ENDPOINT_URL",
            "http://localhost:9000"
        )
        self.access_key = access_key or os.getenv(
            "MINIO_ACCESS_KEY",
            "rckg_admin"
        )
        self.secret_key = secret_key or os.getenv(
            "MINIO_SECRET_KEY",
            "rckg_secret_password"
        )
        self.region = region or os.getenv("MINIO_REGION", "us-east-1")

        # Configure S3 client with proper settings
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
                max_pool_connections=50,
            ),
        )

        # Create resource for higher-level operations
        self.resource = boto3.resource(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

        # Define bucket names
        self.source_regulations_bucket = "source-regulations"
        self.minio_data_bucket = "minio-data"
        self.markdown_conversions_bucket = "markdown-conversions"
        self.evidence_artifacts_bucket = "evidence-artifacts"

    def _ensure_bucket_exists(self, bucket_name: str) -> None:
        """
        Ensure a bucket exists, creating it if necessary.

        Args:
            bucket_name: Name of the bucket to ensure exists
        """
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            # Bucket doesn't exist, create it
            if self.region == "us-east-1":
                self.client.create_bucket(Bucket=bucket_name)
            else:
                self.client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region}
                )

    def upload_file(
        self,
        bucket: str,
        key: str,
        file_obj: BinaryIO,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a file to the specified bucket.

        Args:
            bucket: Bucket name
            key: Object key (file path within bucket)
            file_obj: File-like object to upload
            content_type: MIME type of the file

        Returns:
            The key of the uploaded object
        """
        self._ensure_bucket_exists(bucket)

        self.client.upload_fileobj(file_obj, bucket, key, ExtraArgs={"ContentType": content_type})
        return key

    def upload_file_from_path(
        self,
        bucket: str,
        local_path: str,
        key: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a file from the local filesystem.

        Args:
            bucket: Bucket name
            local_path: Path to local file
            key: Object key (defaults to basename of local_path)
            content_type: MIME type of the file

        Returns:
            The key of the uploaded object
        """
        self._ensure_bucket_exists(bucket)

        key = key or Path(local_path).name
        self.client.upload_file(local_path, bucket, key, ExtraArgs={"ContentType": content_type})
        return key

    def download_file(
        self,
        bucket: str,
        key: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """
        Download a file from the specified bucket.

        Args:
            bucket: Bucket name
            key: Object key (file path within bucket)
            destination: If provided, save to local file path

        Returns:
            File contents as bytes (if destination not provided)
        """
        if destination:
            self.client.download_file(bucket, key, destination)
            return None

        file_obj = self.client.get_object(Bucket=bucket, Key=key)
        return file_obj["Body"].read()

    def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Generate a presigned URL for object access.

        Args:
            bucket: Bucket name
            key: Object key
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL string
        """
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    def delete_file(self, bucket: str, key: str) -> None:
        """
        Delete a file from the specified bucket.

        Args:
            bucket: Bucket name
            key: Object key to delete

        Raises:
            ClientError: If deletion fails
        """
        self.client.delete_object(Bucket=bucket, Key=key)

    def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
    ) -> list:
        """
        List files in a bucket.

        Args:
            bucket: Bucket name
            prefix: Optional prefix to filter results

        Returns:
            List of object keys
        """
        response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if "Contents" not in response:
            return []

        return [obj["Key"] for obj in response["Contents"]]

    def file_exists(self, bucket: str, key: str) -> bool:
        """
        Check if a file exists in the specified bucket.

        Args:
            bucket: Bucket name
            key: Object key to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    def get_file_metadata(self, bucket: str, key: str) -> dict:
        """
        Get metadata for a file.

        Args:
            bucket: Bucket name
            key: Object key

        Returns:
            Dictionary with file metadata (size, content type, etc.)
        """
        response = self.client.head_object(Bucket=bucket, Key=key)
        return {
            "key": key,
            "size": response["ContentLength"],
            "content_type": response.get("ContentType", "application/octet-stream"),
            "last_modified": response["LastModified"],
            "etag": response.get("ETag"),
        }

    def create_bucket(self, bucket_name: str) -> None:
        """
        Create a new bucket.

        Args:
            bucket_name: Name of the bucket to create
        """
        self._ensure_bucket_exists(bucket_name)

    def delete_bucket(self, bucket_name: str) -> None:
        """
        Delete a bucket and all its contents.

        Args:
            bucket_name: Name of the bucket to delete
        """
        # First delete all objects in the bucket
        objects = self.client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            self.client.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": obj["Key"]} for obj in objects["Contents"]]}
            )

        # Then delete the bucket
        self.client.delete_bucket(Bucket=bucket_name)

    def list_buckets(self) -> list:
        """
        List all buckets.

        Returns:
            List of bucket names
        """
        response = self.client.list_buckets()
        return [b["Name"] for b in response.get("Buckets", [])]


# Singleton instance for convenience
_minio_storage_instance: Optional[MinIOStorage] = None


def get_minio_storage() -> MinIOStorage:
    """
    Get the singleton MinIO storage instance.

    Returns:
        MinIOStorage instance configured from environment variables
    """
    global _minio_storage_instance
    if _minio_storage_instance is None:
        _minio_storage_instance = MinIOStorage()
    return _minio_storage_instance


__all__ = [
    "MinIOStorage",
    "get_minio_storage",
]
