#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List

from mcp.server.fastmcp import FastMCP

# Try to import PyGithub
try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not installed. GitHub features will be disabled.", file=sys.stderr)
    print("Install with: pip install PyGithub", file=sys.stderr)

# Create the FastMCP server
mcp = FastMCP("unified-filesystem-github-server")

# Get the working directory
WORKING_DIR = Path.cwd()

# Initialize GitHub client if available
def get_github_client():
    if not GITHUB_AVAILABLE:
        raise RuntimeError("PyGithub not installed")
    
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set")
    return Github(token)


# ========== FILESYSTEM TOOLS ==========

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


# ========== GITHUB TOOLS ==========

@mcp.tool()
def gh_list_repositories(user: Optional[str] = None) -> str:
    """List GitHub repositories for the authenticated user or a specified user.
    
    Args:
        user: GitHub username (optional, defaults to authenticated user)
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        g = get_github_client()
        
        if user:
            repos = g.get_user(user).get_repos()
        else:
            repos = g.get_user().get_repos()
        
        repo_list = []
        for repo in repos:
            repo_list.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            })
        
        return f"Found {len(repo_list)} repositories:\n{json.dumps(repo_list, indent=2)}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def gh_read_file(owner: str, repo: str, path: str, branch: Optional[str] = None) -> str:
    """Read the contents of a file from a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path to the file in the repository
        branch: Branch name (optional, defaults to default branch)
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        if branch:
            file_content = repository.get_contents(path, ref=branch)
        else:
            file_content = repository.get_contents(path)
        
        if isinstance(file_content, list):
            return f"Error: {path} is a directory, not a file"
        
        if file_content.encoding != "base64":
            return f"Error: Unsupported encoding: {file_content.encoding}"
        
        try:
            content = file_content.decoded_content.decode('utf-8')
            return f"Content of {path} from {owner}/{repo}:\n\n{content}"
        except UnicodeDecodeError:
            return f"File {path} appears to be binary (size: {file_content.size} bytes). Cannot display as text."
            
    except GithubException as e:
        if e.status == 404:
            return f"Error: File not found: {path}"
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def gh_list_files(owner: str, repo: str, path: str = "", branch: Optional[str] = None) -> str:
    """List files and directories in a GitHub repository path.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path in the repository (optional, defaults to root)
        branch: Branch name (optional, defaults to default branch)
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        if branch:
            contents = repository.get_contents(path, ref=branch)
        else:
            contents = repository.get_contents(path)
        
        if not isinstance(contents, list):
            contents = [contents]
        
        files = []
        for content in contents:
            files.append({
                "name": content.name,
                "path": content.path,
                "type": content.type,  # "file" or "dir"
                "size": content.size if content.type == "file" else None,
                "sha": content.sha
            })
        
        files.sort(key=lambda x: (x["type"] != "dir", x["name"]))
        
        return f"Files in {owner}/{repo}/{path}:\n{json.dumps(files, indent=2)}"
        
    except GithubException as e:
        if e.status == 404:
            return f"Error: Path not found: {path}"
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def gh_create_or_update_file(owner: str, repo: str, path: str, content: str, 
                            message: str, branch: Optional[str] = None) -> str:
    """Create or update a file in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path for the file in the repository
        content: Content to write to the file
        message: Commit message
        branch: Branch name (optional, defaults to default branch)
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        # Check if file exists
        try:
            existing_file = repository.get_contents(path, ref=branch)
            sha = existing_file.sha
            
            # Update existing file
            result = repository.update_file(
                path=path,
                message=message,
                content=content,
                sha=sha,
                branch=branch
            )
            
            return f"Successfully updated {path} in {owner}/{repo}\nCommit: {result['commit'].sha}"
            
        except GithubException as e:
            if e.status == 404:
                # Create new file
                result = repository.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=branch
                )
                
                return f"Successfully created {path} in {owner}/{repo}\nCommit: {result['commit'].sha}"
            else:
                raise
                
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


# ========== UNIFIED TOOLS ==========

@mcp.tool()
def sync_github_to_local(owner: str, repo: str, github_path: str, local_path: str) -> str:
    """Download a file from GitHub to the local filesystem.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        github_path: Path to the file in GitHub
        local_path: Local path where to save the file
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        # First, read from GitHub
        result = gh_read_file(owner, repo, github_path)
        
        if result.startswith("Error:"):
            return result
        
        # Extract content (remove the "Content of X from Y:" prefix)
        lines = result.split('\n')
        content = '\n'.join(lines[2:]) if len(lines) > 2 else ""
        
        # Write to local file
        write_result = write_file(local_path, content)
        
        if write_result.startswith("Error:"):
            return write_result
            
        return f"Successfully synced {owner}/{repo}/{github_path} to {local_path}"
        
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def sync_local_to_github(local_path: str, owner: str, repo: str, github_path: str, 
                        message: str, branch: Optional[str] = None) -> str:
    """Upload a local file to GitHub.
    
    Args:
        local_path: Path to the local file
        owner: Repository owner (username or organization)
        repo: Repository name
        github_path: Path where to save in GitHub
        message: Commit message
        branch: Branch name (optional)
    """
    if not GITHUB_AVAILABLE:
        return "Error: GitHub features not available. Install PyGithub with: pip install PyGithub"
        
    try:
        # First, read from local
        result = read_file(local_path)
        
        if result.startswith("Error:"):
            return result
        
        # Extract content (remove the "Content of X:" prefix)
        lines = result.split('\n')
        content = '\n'.join(lines[2:]) if len(lines) > 2 else ""
        
        # Upload to GitHub
        gh_result = gh_create_or_update_file(owner, repo, github_path, content, message, branch)
        
        if gh_result.startswith("Error:"):
            return gh_result
            
        return f"Successfully synced {local_path} to {owner}/{repo}/{github_path}"
        
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    try:
        print(f"Starting Unified Filesystem & GitHub MCP Server...", file=sys.stderr)
        print(f"Working directory: {WORKING_DIR}", file=sys.stderr)
        
        if GITHUB_AVAILABLE and os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
            try:
                g = Github(os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'])
                print(f"GitHub user: {g.get_user().login}", file=sys.stderr)
            except:
                print("GitHub token present but could not verify", file=sys.stderr)
        else:
            print("GitHub features disabled (set GITHUB_PERSONAL_ACCESS_TOKEN to enable)", file=sys.stderr)
            
        mcp.run()
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}", file=sys.stderr)
        sys.exit(1)
