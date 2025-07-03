# MS File Server

A scalable file server built with **FastAPI** and **MinIO** for the Microsoft Azure Map Backend Internship assignment. This project demonstrates modern cloud-native architecture with containerization, object storage, and REST API design.

## 🏗️ Architecture

- **API Server**: FastAPI with async/await support
- **Storage Backend**: MinIO (S3-compatible object storage)
- **Containerization**: Docker & Docker Compose
- **CLI Tool**: Python Click-based command-line interface
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## 🚀 Features

### File Operations
- ✅ **Upload File**: Upload files with automatic conflict detection
- ✅ **Download File**: Download files with proper content types
- ✅ **List Files**: View all stored files with metadata
- ✅ **Delete File**: Remove files from storage
- ✅ **File Info**: Get detailed file metadata

### Advanced Features
- 🔄 **Concurrent Request Handling**: Async FastAPI handles multiple requests efficiently
- 📏 **File Size Validation**: Configurable maximum file size limits
- 🛡️ **Error Handling**: Comprehensive error responses with proper HTTP status codes
- 📊 **Health Checks**: Built-in health monitoring endpoints
- 📚 **API Documentation**: Interactive Swagger UI at `/docs`
- 🌐 **CORS Support**: Cross-origin resource sharing enabled
- 🔧 **Environment Configuration**: Flexible configuration via environment variables

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Git

## 🛠️ Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd MS-File-Server
```

### 2. Start with Docker Compose
```bash
# Start all services (MinIO + File Server)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Verify Installation
```bash
# Check server health
curl http://localhost:8080/health

# Access MinIO Console (optional)
# Navigate to http://localhost:9001
# Username: minioadmin
# Password: minioadmin123
```

### 4. Access API Documentation
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## 🖥️ CLI Usage

The CLI tool provides an intuitive interactive interface for file operations:

### Installation
```bash
# Install CLI dependencies
pip install -r requirements.txt

# Make CLI executable (optional)
chmod +x cli.py
```

### Starting the Interactive CLI

```bash
# Start the interactive CLI
python cli.py

# The CLI will prompt you for server URL (default: http://localhost:8080)
# Then display a menu with available options
```

### Interactive Menu

Once started, you'll see an interactive menu:

```
============================================================
🚀 MS File Server - Interactive CLI Tool
============================================================
Welcome to the Microsoft Azure Map Backend File Server!

🌐 Enter server URL (press Enter for http://localhost:8080): 
🔗 Connected to: http://localhost:8080
✅ Server connection successful!

📋 Available Commands:
  1. Upload file
  2. Download file
  3. List all files
  4. Delete file
  5. Get file info
  6. Check server health
  7. Help
  8. Exit
----------------------------------------
👉 Enter your choice (1-8): 
```

### Command Examples

**1. Upload File:**
- Select option `1`
- Enter file path: `/path/to/your/file.txt`
- System uploads and shows confirmation

**2. Download File:**
- Select option `2`
- Enter filename: `file.txt`
- Enter output path (optional): `/path/to/save/`

**3. List Files:**
- Select option `3`
- View formatted table of all files

**4. Delete File:**
- Select option `4`
- Enter filename: `file.txt`
- Confirm deletion: `yes`

**5. Get File Info:**
- Select option `5`
- Enter filename: `file.txt`
- View detailed file metadata

**6. Health Check:**
- Select option `6`
- Check server connectivity and status

**7. Help:**
- Select option `7`
- View detailed command descriptions

**8. Exit:**
- Select option `8`
- Safely exit the application

### Features

- 🎯 **Interactive Interface**: No need to remember command syntax
- 🔗 **Dynamic Server Connection**: Choose server URL at startup
- ✅ **Input Validation**: Prevents empty inputs and invalid choices
- 🛡️ **Safe Operations**: Confirmation required for destructive actions
- 🎨 **Rich Output**: Emojis and formatting for better user experience
- ⌨️ **Keyboard Interrupt**: Graceful exit with Ctrl+C
- 📊 **Formatted Display**: Human-readable file sizes and organized tables

## 🔧 Configuration

Configuration is handled through environment variables:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

### Available Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO server endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin123` | MinIO secret key |
| `MINIO_BUCKET` | `files` | Storage bucket name |
| `MINIO_USE_SSL` | `false` | Enable SSL for MinIO |
| `SERVER_PORT` | `8080` | API server port |
| `SERVER_HOST` | `0.0.0.0` | API server host |
| `MAX_FILE_SIZE` | `104857600` | Max file size in bytes (100MB) |

## 🚀 API Endpoints

### Core File Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/files/upload` | Upload a file |
| `GET` | `/api/v1/files/download/{filename}` | Download a file |
| `GET` | `/api/v1/files` | List all files |
| `DELETE` | `/api/v1/files/{filename}` | Delete a file |
| `GET` | `/api/v1/files/{filename}/info` | Get file metadata |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc documentation |

### Example API Usage

```bash
# Upload a file
curl -X POST "http://localhost:8080/api/v1/files/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.txt"

# List files
curl -X GET "http://localhost:8080/api/v1/files"

# Download a file
curl -X GET "http://localhost:8080/api/v1/files/download/example.txt" \
     --output downloaded_file.txt

# Delete a file
curl -X DELETE "http://localhost:8080/api/v1/files/example.txt"
```

## 🏗️ Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MinIO only
docker-compose up minio -d

# Run server locally
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Project Structure

```
MS-File-Server/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   └── storage.py           # MinIO client wrapper
├── cli.py                   # Command-line interface
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## 🧪 Testing

### Manual Testing

```bash
# Create a test file
echo "Hello World" > test.txt

# Start interactive CLI
python cli.py

# Follow the interactive prompts:
# 1. Choose option 1 (Upload file)
# 2. Enter: test.txt
# 3. Choose option 3 (List all files) 
# 4. Choose option 5 (Get file info) and enter: test.txt
# 5. Choose option 2 (Download file) and enter: test.txt
# 6. Choose option 4 (Delete file) and enter: test.txt
# 7. Choose option 8 (Exit)
```

### Health Monitoring

```bash
# Check API health
curl http://localhost:8080/health

# Check MinIO health
curl http://localhost:9000/minio/health/live
```

## 🐳 Docker Operations

### Build and Run

```bash
# Build and start all services
docker-compose up --build

# Rebuild specific service
docker-compose build file-server

# View logs
docker-compose logs -f file-server

# Stop services
docker-compose down

# Clean up volumes (⚠️ This will delete stored files)
docker-compose down -v
```

### Individual Service Management

```bash
# Start only MinIO
docker-compose up minio -d

# Start only file server (requires MinIO running)
docker-compose up file-server
```
