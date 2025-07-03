import io
from typing import List, Optional, BinaryIO
from datetime import datetime
import logging
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FileInfo(BaseModel):
    name: str
    size: int
    last_modified: str
    content_type: str = "application/octet-stream"


class MinIOStorage:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, 
                 bucket_name: str, secure: bool = False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._ensure_bucket()
    
    def _ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    async def upload_file(self, file_name: str, file_data: BinaryIO, 
                         file_size: int, content_type: str = "application/octet-stream") -> bool:
        """Upload a file to MinIO"""
        try:
            self.client.put_object(
                self.bucket_name,
                file_name,
                file_data,
                file_size,
                content_type=content_type
            )
            logger.info(f"Successfully uploaded: {file_name}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading file {file_name}: {e}")
            raise
    
    async def download_file(self, file_name: str) -> Optional[BinaryIO]:
        """Download a file from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            return response
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            logger.error(f"Error downloading file {file_name}: {e}")
            raise
    
    async def list_files(self) -> List[FileInfo]:
        """List all files in the bucket"""
        try:
            files = []
            objects = self.client.list_objects(self.bucket_name)
            
            for obj in objects:
                # Get additional file info
                stat = self.client.stat_object(self.bucket_name, obj.object_name)
                
                files.append(FileInfo(
                    name=obj.object_name,
                    size=obj.size,
                    last_modified=obj.last_modified.strftime("%Y-%m-%d %H:%M:%S"),
                    content_type=stat.content_type or "application/octet-stream"
                ))
            
            return files
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            raise
    
    async def delete_file(self, file_name: str) -> bool:
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"Successfully deleted: {file_name}")
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"Error deleting file {file_name}: {e}")
            raise
    
    async def file_exists(self, file_name: str) -> bool:
        """Check if a file exists"""
        try:
            self.client.stat_object(self.bucket_name, file_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"Error checking file existence {file_name}: {e}")
            raise
    
    async def get_file_info(self, file_name: str) -> Optional[FileInfo]:
        """Get file metadata"""
        try:
            stat = self.client.stat_object(self.bucket_name, file_name)
            return FileInfo(
                name=file_name,
                size=stat.size,
                last_modified=stat.last_modified.strftime("%Y-%m-%d %H:%M:%S"),
                content_type=stat.content_type or "application/octet-stream"
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            logger.error(f"Error getting file info {file_name}: {e}")
            raise 