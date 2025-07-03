#!/usr/bin/env python3
"""
Example test script to demonstrate the file server functionality using REST API
Note: The CLI is now interactive, so this script tests the API directly
"""

import os
import requests
import sys
from pathlib import Path
import json


class FileServerClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def health_check(self) -> bool:
        """Check server health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    def upload_file(self, file_path: str) -> dict:
        """Upload a file to the server"""
        file_path = Path(file_path)
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(f"{self.api_base}/files/upload", files=files)
        response.raise_for_status()
        return response.json()
    
    def list_files(self) -> list:
        """List all files on the server"""
        response = requests.get(f"{self.api_base}/files")
        response.raise_for_status()
        return response.json()
    
    def get_file_info(self, filename: str) -> dict:
        """Get file information"""
        response = requests.get(f"{self.api_base}/files/{filename}/info")
        response.raise_for_status()
        return response.json()
    
    def download_file(self, filename: str, output_path: str) -> None:
        """Download a file from the server"""
        response = requests.get(f"{self.api_base}/files/download/{filename}")
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
    
    def delete_file(self, filename: str) -> dict:
        """Delete a file from the server"""
        response = requests.delete(f"{self.api_base}/files/{filename}")
        response.raise_for_status()
        return response.json()


def create_test_files():
    """Create some test files"""
    test_files = [
        ("test1.txt", "Hello World from Test File 1"),
        ("test2.json", '{"message": "Hello from JSON file", "timestamp": "2024-01-01"}'),
        ("test3.md", "# Test Markdown File\n\nThis is a test markdown file for the file server demo.")
    ]
    
    for filename, content in test_files:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Created test file: {filename}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = size_bytes
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def main():
    """Main test function"""
    print("🧪 MS File Server API Test Demo")
    print("=" * 55)
    print("Note: This script tests the API directly.")
    print("For interactive testing, use: python cli.py")
    print("=" * 55)
    
    # Initialize client
    client = FileServerClient()
    
    # Check if server is running
    print("\n1. 🔍 Checking server health...")
    if not client.health_check():
        print("❌ Server is not running. Please start it with: docker-compose up -d")
        sys.exit(1)
    print("✅ Server is healthy!")
    
    # Create test files
    print("\n2. 📁 Creating test files...")
    create_test_files()
    
    # Upload files
    print("\n3. 📤 Uploading test files...")
    for filename in ["test1.txt", "test2.json", "test3.md"]:
        try:
            result = client.upload_file(filename)
            print(f"✅ Uploaded: {result['filename']} ({format_file_size(result['size'])})")
        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")
    
    # List files
    print("\n4. 📋 Listing all files on server...")
    try:
        files = client.list_files()
        print(f"Found {len(files)} file(s):")
        print(f"{'Name':<20} {'Size':<10} {'Last Modified':<20} {'Content Type':<20}")
        print("-" * 75)
        for file_info in files:
            size_str = format_file_size(file_info['size'])
            print(f"{file_info['name']:<20} {size_str:<10} {file_info['last_modified']:<20} {file_info['content_type']:<20}")
    except Exception as e:
        print(f"❌ Failed to list files: {e}")
    
    # Get file info
    print("\n5. ℹ️ Getting file information...")
    try:
        file_info = client.get_file_info("test1.txt")
        print(f"File Information for 'test1.txt':")
        print(f"  📝 Name: {file_info['name']}")
        print(f"  📏 Size: {format_file_size(file_info['size'])}")
        print(f"  📅 Last Modified: {file_info['last_modified']}")
        print(f"  📄 Content Type: {file_info['content_type']}")
    except Exception as e:
        print(f"❌ Failed to get file info: {e}")
    
    # Download a file
    print("\n6. 📥 Downloading a file...")
    try:
        client.download_file("test2.json", "downloaded_test2.json")
        print("✅ File downloaded successfully")
        
        # Verify download
        if Path("downloaded_test2.json").exists():
            with open("downloaded_test2.json", 'r') as f:
                content = f.read()
                print(f"📄 Downloaded content: {content}")
        else:
            print("❌ Downloaded file not found")
    except Exception as e:
        print(f"❌ Failed to download file: {e}")
    
    # Clean up local files
    print("\n7. 🧹 Cleaning up local test files...")
    for filename in ["test1.txt", "test2.json", "test3.md", "downloaded_test2.json"]:
        if Path(filename).exists():
            os.remove(filename)
            print(f"🗑️ Removed: {filename}")
    
    print("\n✅ API Test completed successfully!")
    print("\n📝 Next steps:")
    print("1. Start the interactive CLI: python cli.py")
    print("2. Access API docs: http://localhost:8080/docs")
    print("3. Access MinIO console: http://localhost:9001")
    print("\n🗑️ To delete test files from server:")
    print("   - Use the interactive CLI (option 4)")
    print("   - Or call DELETE /api/v1/files/{filename}")


if __name__ == "__main__":
    main() 