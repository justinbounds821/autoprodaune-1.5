"""Filesystem operations tool"""

from __future__ import annotations

from pathlib import Path


def fs_write_file(path: Path, content: str) -> int:
    """
    Write file to filesystem

    Args:
        path: File path
        content: File content

    Returns:
        Number of bytes written
    """
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content if isinstance(content, str) else str(content)
    path.write_text(data, encoding="utf-8")
    return len(data)


def fs_read_file(path: Path) -> str:
    """
    Read file from filesystem

    Args:
        path: File path

    Returns:
        File content

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = path.resolve()
    return path.read_text(encoding="utf-8")
