# -*- coding: utf-8 -*-
# https://github.com/Longdh57/fastapi-minio

from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from pydantic import BaseModel

from app.utils import uuid7


class IMinioResponse(BaseModel):
    bucket_name: str
    file_name: str
    url: str


class MinioClient:
    """Minio client."""

    def __init__(
        self,
        minio_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
    ):
        self.minio_url = minio_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()

    def make_bucket(
        self,
    ) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name

    def presigned_get_object(
        self,
        bucket_name: str,
        object_name: str,
    ) -> str:
        # Request URL expired after 7 days
        url = self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=7),
        )
        return url

    def put_object(
        self,
        file_data: BinaryIO,
        file_name: str,
        content_type: str,
    ) -> IMinioResponse:
        """Put an object in the bucket."""
        try:
            object_name = f"{uuid7()}{file_name}"
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=10 * 1024 * 1024,
            )
            url = self.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
            )
            data_file = IMinioResponse(
                bucket_name=self.bucket_name,
                file_name=object_name,
                url=url,
            )
            return data_file
        except Exception as e:
            raise e
