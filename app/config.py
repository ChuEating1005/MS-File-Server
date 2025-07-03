import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MinIO Configuration
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "files"
    minio_use_ssl: bool = False
    
    # Server Configuration
    server_port: int = 8080
    server_host: str = "0.0.0.0"
    
    # Application Configuration
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  


# Global settings instance
settings = Settings() 