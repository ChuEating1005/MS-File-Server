#!/usr/bin/env python3
"""
Interactive File Server CLI Tool
A command-line interface for interacting with the MS File Server
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional


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
    print("Welcome to the Microsoft File Server!")
    print("")


def print_commands():
    """Print available commands"""
    print("\n📋 Available Commands:")
    print("  upload <file_path>    - Upload a file to the server")
    print("  download <file_name>  - Download a file from the server") 
    print("  list                  - List all files on the server")
    print("  delete <file_name>    - Delete a file from the server")
    print("  help                  - Show this help message")
    print("  exit                  - Exit the application")
    print("-" * 50)


def handle_upload(client: FileServerClient, file_path: str):
    """Handle file upload"""
    if not file_path:
        print("❌ Error: Please specify a file path. Usage: upload <file_path>")
        return
    
    try:
        print(f"Uploading {file_path}...")
        result = client.upload_file(file_path)
        print(f"✅ {result['message']}")
        print(f"   📏 Size: {format_file_size(result['size'])}")
        print(f"   📄 Content Type: {result['content_type']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_download(client: FileServerClient, filename: str):
    """Handle file download"""
    if not filename:
        print("❌ Error: Please specify a filename. Usage: download <file_name>")
        return
    
    try:
        print(f"Downloading {filename}...")
        result_path = client.download_file(filename)
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


def handle_delete(client: FileServerClient, filename: str):
    """Handle file deletion"""
    if not filename:
        print("❌ Error: Please specify a filename. Usage: delete <file_name>")
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





def parse_command(command_line: str):
    """Parse command line input into command and arguments"""
    parts = command_line.strip().split(None, 1)
    if not parts:
        return None, None
    
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return command, args


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
        try:
            client.health_check()
            print("✅ Server connection successful!")
        except:
            print("⚠️ Warning: Could not verify server connection, but proceeding...")
        
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        print("Please make sure the server is running and try again.")
        return
    
    # Show available commands
    print_commands()
    
    # Main interactive loop
    while True:
        try:
            command_line = input("\n$ ").strip()
            
            if not command_line:
                continue
                
            command, args = parse_command(command_line)
            
            if command == 'upload':
                handle_upload(client, args)
            elif command == 'download':
                handle_download(client, args)
            elif command == 'list':
                handle_list(client)
            elif command == 'delete':
                handle_delete(client, args)
            elif command == 'help':
                print_commands()
            elif command in ['exit', 'quit']:
                print("\n👋 Thank you for using MS File Server CLI!")
                print("Goodbye! 🚀")
                break
            else:
                print(f"❌ Unknown command: {command}")
                print("💡 Type 'help' to see available commands.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye! 🚀")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Please try again or contact support.")


if __name__ == '__main__':
    main() 