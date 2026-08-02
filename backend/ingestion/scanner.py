import os
from typing import List, Dict, Any

class DocumentScanner:
    """
    DocumentScanner scans a directory recursively, gathers metadata for all files,
    and identifies their formats (PDF, Excel, Word, JSON, etc.).
    """
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.docx': 'docx',
        '.doc': 'docx',
        '.json': 'json'
    }

    @staticmethod
    def get_file_size_display(size_bytes: int) -> str:
        """
        Formats a file size from bytes into a human-readable display string (e.g. 1.2 MB).
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                # Format to 1 decimal place unless it's just bytes
                if unit == 'B':
                    return f"{size_bytes} {unit}"
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def scan(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Recursively scans directory_path, skipping hidden directories/files,
        and returns a list of files with their parsed metadata.
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Target scan directory '{directory_path}' does not exist.")

        file_list = []
        for root, dirs, files in os.walk(directory_path):
            # Exclude hidden directories (starting with '.') or standard python system cache folders
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.startswith('.'):
                    continue

                full_path = os.path.join(root, file)
                extension = os.path.splitext(file)[1].lower()
                file_type = self.SUPPORTED_EXTENSIONS.get(extension, 'unknown')

                try:
                    size_bytes = os.path.getsize(full_path)
                    size_display = self.get_file_size_display(size_bytes)
                except OSError:
                    size_bytes = 0
                    size_display = "0 B"

                # Normalize paths to use forward slashes for cross-platform compatibility
                relative_path = os.path.relpath(full_path, directory_path).replace(os.sep, '/')
                absolute_path = os.path.abspath(full_path).replace(os.sep, '/')

                file_list.append({
                    "name": file,
                    "type": file_type,
                    "size_bytes": size_bytes,
                    "size_display": size_display,
                    "path": relative_path,
                    "absolute_path": absolute_path,
                    "extension": extension
                })
        
        return file_list
