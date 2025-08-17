"""Filesystem tool for MCP - Safe file operations."""

import os
from pathlib import Path
from typing import Any


class FilesystemTool:
    """Safe filesystem operations for AI agents."""

    def __init__(self, config: dict[str, Any]):
        """Initialize filesystem tool.

        Args:
            config: Tool configuration
        """
        self.config = config
        self.permissions = config.get("permissions", {})
        self.workspace = Path(os.getenv("WORKSPACE_DIR", "/tmp/workspace"))

    def validate_path(self, path: Path, operation: str) -> bool:
        """Validate path against security rules.

        Args:
            path: Path to validate
            operation: Operation type (read/write)

        Returns:
            True if path is allowed
        """
        path = path.resolve()

        # Check allowed paths
        allowed = self.permissions.get(operation, {}).get("allowed_paths", [])
        denied = self.permissions.get(operation, {}).get("denied_paths", [])

        # Check if path matches any denied pattern
        for pattern in denied:
            if path.match(pattern):
                return False

        # Check if path matches any allowed pattern
        for pattern in allowed:
            if path.match(pattern):
                return True

        return False

    async def read_file(self, path: str) -> str:
        """Read file contents safely.

        Args:
            path: File path to read

        Returns:
            File contents

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(path).resolve()

        if not self.validate_path(file_path, "read"):
            raise PermissionError(f"Reading from {path} is not allowed")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return file_path.read_text()

    async def write_file(self, path: str, content: str) -> None:
        """Write file contents safely.

        Args:
            path: File path to write
            content: Content to write

        Raises:
            PermissionError: If path is not allowed
        """
        file_path = Path(path).resolve()

        if not self.validate_path(file_path, "write"):
            raise PermissionError(f"Writing to {path} is not allowed")

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        file_path.write_text(content)

    async def list_directory(self, path: str = ".") -> list[dict[str, Any]]:
        """List directory contents safely.

        Args:
            path: Directory path to list

        Returns:
            List of file/directory information

        Raises:
            PermissionError: If path is not allowed
            NotADirectoryError: If path is not a directory
        """
        dir_path = Path(path).resolve()

        if not self.validate_path(dir_path, "read"):
            raise PermissionError(f"Listing {path} is not allowed")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        items = []
        for item in dir_path.iterdir():
            items.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "is_file": item.is_file(),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime,
                }
            )

        return items

    async def create_directory(self, path: str) -> None:
        """Create directory safely.

        Args:
            path: Directory path to create

        Raises:
            PermissionError: If path is not allowed
        """
        dir_path = Path(path).resolve()

        if not self.validate_path(dir_path, "write"):
            raise PermissionError(f"Creating {path} is not allowed")

        dir_path.mkdir(parents=True, exist_ok=True)

    async def delete_file(self, path: str) -> None:
        """Delete file safely.

        Args:
            path: File path to delete

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(path).resolve()

        if not self.validate_path(file_path, "write"):
            raise PermissionError(f"Deleting {path} is not allowed")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if file_path.is_file():
            file_path.unlink()
        else:
            raise IsADirectoryError(f"Cannot delete directory: {path}")

    async def move_file(self, source: str, destination: str) -> None:
        """Move file safely.

        Args:
            source: Source file path
            destination: Destination file path

        Raises:
            PermissionError: If paths are not allowed
            FileNotFoundError: If source doesn't exist
        """
        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()

        if not self.validate_path(src_path, "read"):
            raise PermissionError(f"Reading from {source} is not allowed")

        if not self.validate_path(dst_path, "write"):
            raise PermissionError(f"Writing to {destination} is not allowed")

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # Create destination directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        src_path.rename(dst_path)

    async def copy_file(self, source: str, destination: str) -> None:
        """Copy file safely.

        Args:
            source: Source file path
            destination: Destination file path

        Raises:
            PermissionError: If paths are not allowed
            FileNotFoundError: If source doesn't exist
        """
        import shutil

        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()

        if not self.validate_path(src_path, "read"):
            raise PermissionError(f"Reading from {source} is not allowed")

        if not self.validate_path(dst_path, "write"):
            raise PermissionError(f"Writing to {destination} is not allowed")

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # Create destination directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(src_path, dst_path)

    async def get_file_info(self, path: str) -> dict[str, Any]:
        """Get file information safely.

        Args:
            path: File path

        Returns:
            File information dictionary

        Raises:
            PermissionError: If path is not allowed
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(path).resolve()

        if not self.validate_path(file_path, "read"):
            raise PermissionError(f"Accessing {path} is not allowed")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stat = file_path.stat()

        return {
            "name": file_path.name,
            "path": str(file_path),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "permissions": oct(stat.st_mode)[-3:],
            "owner": stat.st_uid,
            "group": stat.st_gid,
        }
