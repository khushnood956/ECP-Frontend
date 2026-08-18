from typing import Protocol

import boto3  # type: ignore
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError  # type: ignore

from app.core.config.settings import settings


class StorageService(Protocol):
    async def upload(self, file_content: bytes, object_key: str, content_type: str) -> bool:
        ...

    async def delete(self, object_key: str) -> bool:
        ...

    async def generate_download_url(self, object_key: str, filename: str, expires_in: int = 3600) -> str:
        ...


class S3StorageService:
    def __init__(self) -> None:
        session_kwargs = {}
        if settings.AWS_ACCESS_KEY_ID:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        if settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        if settings.AWS_REGION:
            session_kwargs["region_name"] = settings.AWS_REGION

        self.s3_client = boto3.client("s3", **session_kwargs)
        self.bucket = settings.AWS_S3_BUCKET

    async def upload(self, file_content: bytes, object_key: str, content_type: str) -> bool:
        try:
            # Running synchronous boto3 call in executor can be considered, but for simple app inline is standard.
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=file_content,
                ContentType=content_type
            )
            return True
        except (ClientError, BotoCoreError, NoCredentialsError, EndpointConnectionError) as e:
            print(f"Failed S3 upload: {e}")
            return False

    async def delete(self, object_key: str) -> bool:
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=object_key
            )
            return True
        except (ClientError, BotoCoreError, NoCredentialsError, EndpointConnectionError) as e:
            print(f"Failed S3 delete: {e}")
            return False

    async def generate_download_url(self, object_key: str, filename: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": object_key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"'
                },
                ExpiresIn=expires_in
            )
            return url
        except (ClientError, BotoCoreError, NoCredentialsError, EndpointConnectionError) as e:
            print(f"Failed S3 presign: {e}")
            return ""
