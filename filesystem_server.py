#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

# Create the FastMCP server
mcp = FastMCP("simple-file-server")

# Get the working directory (you can change this)
WORKING_DIR = Path.cwd()


@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files and directories in a given path.

    Args:
        directory: Directory path to list (relative to working directory)
    """
    try:
        full_path = (WORKING_DIR / directory).resolve()

        # Security check - ensure we stay within working directory
        if not str(full_path).startswith(str(WORKING_DIR)):
            return "Error: Access denied - Cannot access files outside working directory"

        if not full_path.exists():
            return f"Error: Directory does not exist: {directory}"

        if not full_path.is_dir():
            return f"Error: Path is not a directory: {directory}"

        files = []
        for item in full_path.iterdir():
            files.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })

        # Sort files by name
        files.sort(key=lambda x: x["name"])

        return f"Files in {directory}:\n" + json.dumps(files, indent=2)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def read_file(filepath: str) -> str:
    """Read the contents of a text file.

    Args:
        filepath: Path to the file to read (relative to working directory)
    """
    try:
        full_path = (WORKING_DIR / filepath).resolve()

        # Security check
        if not str(full_path).startswith(str(WORKING_DIR)):
            return "Error: Access denied - Cannot access files outside working directory"

        if not full_path.exists():
            return f"Error: File does not exist: {filepath}"

        if not full_path.is_file():
            return f"Error: Path is not a file: {filepath}"

        try:
            content = full_path.read_text(encoding='utf-8')
            return f"Content of {filepath}:\n\n{content}"
        except UnicodeDecodeError:
            # Try to read as binary and show info
            size = full_path.stat().st_size
            return f"File {filepath} appears to be binary (size: {size} bytes). Cannot display as text."

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.

    Args:
        filepath: Path to the file to write (relative to working directory)
        content: Content to write to the file
    """
    try:
        full_path = (WORKING_DIR / filepath).resolve()

        # Security check
        if not str(full_path).startswith(str(WORKING_DIR)):
            return "Error: Access denied - Cannot access files outside working directory"

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        full_path.write_text(content, encoding='utf-8')

        return f"Successfully wrote {len(content)} characters to {filepath}"

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_directory(directory: str) -> str:
    """Create a new directory.

    Args:
        directory: Directory path to create (relative to working directory)
    """
    try:
        full_path = (WORKING_DIR / directory).resolve()

        # Security check
        if not str(full_path).startswith(str(WORKING_DIR)):
            return "Error: Access denied - Cannot access files outside working directory"

        full_path.mkdir(parents=True, exist_ok=True)

        return f"Successfully created directory: {directory}"

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_working_directory() -> str:
    """Get information about the current working directory."""
    try:
        file_count = len([f for f in WORKING_DIR.iterdir() if f.is_file()])
        dir_count = len([f for f in WORKING_DIR.iterdir() if f.is_dir()])

        return f"""Working Directory Information:
Path: {WORKING_DIR}
Files: {file_count}
Directories: {dir_count}
Total items: {file_count + dir_count}
"""
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print(f"Starting Simple File MCP Server...", file=sys.stderr)
    print(f"Working directory: {WORKING_DIR}", file=sys.stderr)
    mcp.run()