import logging
import os
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io

from app.config import settings
from app.storage import MinIOStorage, FileInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage instance
storage: MinIOStorage = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    global storage
    storage = MinIOStorage(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.minio_bucket,
        secure=settings.minio_use_ssl
    )
    logger.info("File server started successfully")
    yield
    # Shutdown
    logger.info("File server shutting down")


# Create FastAPI instance
app = FastAPI(
    title="MS File Server",
    description="A scalable file server using FastAPI and MinIO for Microsoft Azure Map Backend Internship",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_storage() -> MinIOStorage:
    """Dependency to get storage instance"""
    if storage is None:
        raise HTTPException(status_code=500, detail="Storage not initialized")
    return storage


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MS File Server is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "file-server"}


@app.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    storage: MinIOStorage = Depends(get_storage)
):
    """Upload a file to the server"""
    try:
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size} bytes"
            )
        
        # Check if file already exists
        if await storage.file_exists(file.filename):
            raise HTTPException(
                status_code=409,
                detail=f"File {file.filename} already exists"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Upload to MinIO
        success = await storage.upload_file(
            file_name=file.filename,
            file_data=io.BytesIO(file_content),
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream"
        )
        
        if success:
            return {
                "message": f"File {file.filename} uploaded successfully",
                "filename": file.filename,
                "size": file_size,
                "content_type": file.content_type
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/files/download/{filename}")
async def download_file(
    filename: str,
    storage: MinIOStorage = Depends(get_storage)
):
    """Download a file from the server"""
    try:
        # Check if file exists
        if not await storage.file_exists(filename):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file info for content type
        file_info = await storage.get_file_info(filename)
        
        # Get file from MinIO
        file_data = await storage.download_file(filename)
        
        if file_data is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(file_data.read()),
            media_type=file_info.content_type if file_info else "application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/files", response_model=List[FileInfo])
async def list_files(storage: MinIOStorage = Depends(get_storage)):
    """List all files stored on the server"""
    try:
        files = await storage.list_files()
        return files
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/files/{filename}")
async def delete_file(
    filename: str,
    storage: MinIOStorage = Depends(get_storage)
):
    """Delete a file from the server"""
    try:
        # Check if file exists
        if not await storage.file_exists(filename):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file
        success = await storage.delete_file(filename)
        
        if success:
            return {"message": f"File {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/files/{filename}/info", response_model=FileInfo)
async def get_file_info(
    filename: str,
    storage: MinIOStorage = Depends(get_storage)
):
    """Get file information"""
    try:
        file_info = await storage.get_file_info(filename)
        if file_info is None:
            raise HTTPException(status_code=404, detail="File not found")
        return file_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server_host, port=settings.server_port) 