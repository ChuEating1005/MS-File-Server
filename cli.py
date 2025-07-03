#!/usr/bin/env python3
"""
Interactive File Server CLI Tool
A command-line interface for interacting with the MS File Server
"""

import os
import sys
import requests
import click
from pathlib import Path
from typing import Optional
import json


class FileServerClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def upload_file(self, file_path: str) -> dict:
        """Upload a file to the server"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            response = requests.post(f"{self.api_base}/files/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 409:
            raise Exception(f"File already exists: {file_path.name}")
        elif response.status_code == 413:
            raise Exception("File too large")
        else:
            response.raise_for_status()
    
    def download_file(self, filename: str, output_path: Optional[str] = None) -> str:
        """Download a file from the server"""
        response = requests.get(f"{self.api_base}/files/download/{filename}")
        
        if response.status_code == 404:
            raise Exception(f"File not found: {filename}")
        elif response.status_code != 200:
            response.raise_for_status()
        
        # Determine output path
        if output_path is None:
            output_path = filename
        
        output_path = Path(output_path)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file content
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return str(output_path)
    
    def list_files(self) -> list:
        """List all files on the server"""
        response = requests.get(f"{self.api_base}/files")
        response.raise_for_status()
        return response.json()
    
    def delete_file(self, filename: str) -> dict:
        """Delete a file from the server"""
        response = requests.delete(f"{self.api_base}/files/{filename}")
        
        if response.status_code == 404:
            raise Exception(f"File not found: {filename}")
        elif response.status_code != 200:
            response.raise_for_status()
        
        return response.json()
    
    def get_file_info(self, filename: str) -> dict:
        """Get file information"""
        response = requests.get(f"{self.api_base}/files/{filename}/info")
        
        if response.status_code == 404:
            raise Exception(f"File not found: {filename}")
        elif response.status_code != 200:
            response.raise_for_status()
        
        return response.json()
    
    def health_check(self) -> dict:
        """Check server health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


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


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🚀 MS File Server - Interactive CLI Tool")
    print("=" * 60)
    print("Welcome to the Microsoft Azure Map Backend File Server!")
    print("")


def print_menu():
    """Print main menu options"""
    print("\n📋 Available Commands:")
    print("  1. Upload file")
    print("  2. Download file") 
    print("  3. List all files")
    print("  4. Delete file")
    print("  5. Get file info")
    print("  6. Check server health")
    print("  7. Help")
    print("  8. Exit")
    print("-" * 40)


def handle_upload(client: FileServerClient):
    """Handle file upload"""
    file_path = input("📤 Enter file path to upload: ").strip()
    if not file_path:
        print("❌ Error: File path cannot be empty")
        return
    
    try:
        print(f"Uploading {file_path}...")
        result = client.upload_file(file_path)
        print(f"✅ {result['message']}")
        print(f"   📏 Size: {format_file_size(result['size'])}")
        print(f"   📄 Content Type: {result['content_type']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_download(client: FileServerClient):
    """Handle file download"""
    filename = input("📥 Enter filename to download: ").strip()
    if not filename:
        print("❌ Error: Filename cannot be empty")
        return
    
    output_path = input("💾 Enter output path (press Enter for current directory): ").strip()
    if not output_path:
        output_path = None
    
    try:
        print(f"Downloading {filename}...")
        result_path = client.download_file(filename, output_path)
        print(f"✅ File downloaded to: {result_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_list(client: FileServerClient):
    """Handle file listing"""
    try:
        files = client.list_files()
        
        if not files:
            print("📭 No files found on the server.")
            return
        
        print(f"\n📂 Found {len(files)} file(s):")
        print("")
        print(f"{'Name':<35} {'Size':<12} {'Last Modified':<20} {'Content Type':<25}")
        print("=" * 95)
        
        for file_info in files:
            size_str = format_file_size(file_info['size'])
            name = file_info['name'][:34] + "..." if len(file_info['name']) > 34 else file_info['name']
            content_type = file_info['content_type'][:24] + "..." if len(file_info['content_type']) > 24 else file_info['content_type']
            
            print(f"{name:<35} {size_str:<12} {file_info['last_modified']:<20} {content_type:<25}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_delete(client: FileServerClient):
    """Handle file deletion"""
    filename = input("🗑️ Enter filename to delete: ").strip()
    if not filename:
        print("❌ Error: Filename cannot be empty")
        return
    
    # Confirmation
    confirm = input(f"⚠️ Are you sure you want to delete '{filename}'? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Deletion cancelled.")
        return
    
    try:
        result = client.delete_file(filename)
        print(f"✅ {result['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_info(client: FileServerClient):
    """Handle file info retrieval"""
    filename = input("ℹ️ Enter filename to get info: ").strip()
    if not filename:
        print("❌ Error: Filename cannot be empty")
        return
    
    try:
        file_info = client.get_file_info(filename)
        
        print("\n📊 File Information:")
        print(f"   📝 Name: {file_info['name']}")
        print(f"   📏 Size: {format_file_size(file_info['size'])} ({file_info['size']:,} bytes)")
        print(f"   📅 Last Modified: {file_info['last_modified']}")
        print(f"   📄 Content Type: {file_info['content_type']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_health(client: FileServerClient):
    """Handle health check"""
    try:
        result = client.health_check()
        print(f"✅ Server Status: {result['status']}")
        print(f"   🔧 Service: {result['service']}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")


def print_help():
    """Print help information"""
    print("\n📖 Help - Command Descriptions:")
    print("=" * 50)
    print("1. Upload file     - Upload a local file to the server")
    print("2. Download file   - Download a file from the server")
    print("3. List all files  - Show all files stored on the server")
    print("4. Delete file     - Remove a file from the server")
    print("5. Get file info   - Display detailed file information")
    print("6. Check health    - Verify server connectivity")
    print("7. Help            - Show this help message")
    print("8. Exit            - Quit the application")
    print("")
    print("💡 Tips:")
    print("- Use relative or absolute file paths for uploads")
    print("- Downloaded files are saved to current directory by default")
    print("- File deletion requires confirmation for safety")


def main():
    """Main interactive loop"""
    print_banner()
    
    # Get server URL
    server_url = input("🌐 Enter server URL (press Enter for http://localhost:8080): ").strip()
    if not server_url:
        server_url = "http://localhost:8080"
    
    # Initialize client
    try:
        client = FileServerClient(server_url)
        print(f"🔗 Connected to: {server_url}")
        
        # Test connection
        client.health_check()
        print("✅ Server connection successful!")
        
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        print("Please make sure the server is running and try again.")
        return
    
    # Main interactive loop
    while True:
        try:
            print_menu()
            choice = input("👉 Enter your choice (1-8): ").strip()
            
            if choice == '1':
                handle_upload(client)
            elif choice == '2':
                handle_download(client)
            elif choice == '3':
                handle_list(client)
            elif choice == '4':
                handle_delete(client)
            elif choice == '5':
                handle_info(client)
            elif choice == '6':
                handle_health(client)
            elif choice == '7':
                print_help()
            elif choice == '8':
                print("\n👋 Thank you for using MS File Server CLI!")
                print("Goodbye! 🚀")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye! 🚀")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Please try again or contact support.")


if __name__ == '__main__':
    main() 