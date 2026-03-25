import os
import glob
from pathlib import Path

def read_file(path: str) -> str:
    """Reads the contents of a file from the disk."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {e}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file, securely creating directories if missing."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote new contents to: {path}"
    except Exception as e:
        return f"Error writing to file {path}: {e}"

def delete_file(path: str) -> str:
    """Deletes a file from the disk."""
    try:
        os.remove(path)
        return f"Successfully deleted {path}"
    except Exception as e:
        return f"Error deleting file {path}: {e}"

def list_dir(path: str = ".") -> str:
    """Lists all files and subdirectories in the specified path."""
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory {path}: {e}"

def search_files(directory: str, pattern: str) -> list:
    """Searches recursively for files matching a glob pattern."""
    try:
        search_path = os.path.join(directory, "**", pattern)
        files = glob.glob(search_path, recursive=True)
        return files
    except Exception as e:
        return [f"Error searching for {pattern}: {e}"]
