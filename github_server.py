#!/usr/bin/env python3

import os
import sys
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# You'll need to install PyGithub
try:
    from github import Github, GithubException
except ImportError:
    print("Error: PyGithub not installed. Run: pip install PyGithub", file=sys.stderr)
    sys.exit(1)

# Create the FastMCP server
mcp = FastMCP("github-file-server")

# Initialize GitHub client
def get_github_client():
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set")
    return Github(token)


@mcp.tool()
def list_repositories(user: Optional[str] = None) -> str:
    """List GitHub repositories for the authenticated user or a specified user.
    
    Args:
        user: GitHub username (optional, defaults to authenticated user)
    """
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
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            })
        
        return f"Found {len(repo_list)} repositories:\n{json.dumps(repo_list, indent=2)}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_repository_info(owner: str, repo: str) -> str:
    """Get detailed information about a specific repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    """
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        info = {
            "name": repository.name,
            "full_name": repository.full_name,
            "description": repository.description,
            "private": repository.private,
            "fork": repository.fork,
            "created_at": repository.created_at.isoformat(),
            "updated_at": repository.updated_at.isoformat(),
            "pushed_at": repository.pushed_at.isoformat() if repository.pushed_at else None,
            "size": repository.size,
            "stars": repository.stargazers_count,
            "watchers": repository.watchers_count,
            "forks": repository.forks_count,
            "open_issues": repository.open_issues_count,
            "language": repository.language,
            "topics": repository.get_topics(),
            "default_branch": repository.default_branch,
            "has_issues": repository.has_issues,
            "has_wiki": repository.has_wiki,
            "has_pages": repository.has_pages,
            "license": repository.license.name if repository.license else None,
            "clone_url": repository.clone_url,
            "ssh_url": repository.ssh_url
        }
        
        return f"Repository {owner}/{repo}:\n{json.dumps(info, indent=2)}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def read_github_file(owner: str, repo: str, path: str, branch: Optional[str] = None) -> str:
    """Read the contents of a file from a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path to the file in the repository
        branch: Branch name (optional, defaults to default branch)
    """
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
def list_github_files(owner: str, repo: str, path: str = "", branch: Optional[str] = None) -> str:
    """List files and directories in a GitHub repository path.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path in the repository (optional, defaults to root)
        branch: Branch name (optional, defaults to default branch)
    """
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
def create_or_update_file(owner: str, repo: str, path: str, content: str, 
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


@mcp.tool()
def search_code(query: str, user: Optional[str] = None, repo: Optional[str] = None) -> str:
    """Search for code across GitHub repositories.
    
    Args:
        query: Search query
        user: Limit search to specific user (optional)
        repo: Limit search to specific repo in format "owner/repo" (optional)
    """
    try:
        g = get_github_client()
        
        # Build search query
        search_query = query
        if user:
            search_query += f" user:{user}"
        if repo:
            search_query += f" repo:{repo}"
        
        # Search code
        code_results = g.search_code(search_query)
        
        results = []
        count = 0
        for code in code_results:
            if count >= 10:  # Limit results
                break
                
            results.append({
                "repository": code.repository.full_name,
                "path": code.path,
                "name": code.name,
                "sha": code.sha,
                "html_url": code.html_url
            })
            count += 1
        
        return f"Found {code_results.totalCount} results (showing first {count}):\n{json.dumps(results, indent=2)}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_issues(owner: str, repo: str, state: str = "open") -> str:
    """List issues in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        state: Issue state - "open", "closed", or "all" (default: "open")
    """
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        issues = repository.get_issues(state=state)
        
        issue_list = []
        count = 0
        for issue in issues:
            if count >= 20:  # Limit results
                break
                
            # Skip pull requests (they're also returned by get_issues)
            if issue.pull_request:
                continue
                
            issue_list.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "author": issue.user.login,
                "assignees": [a.login for a in issue.assignees],
                "labels": [l.name for l in issue.labels],
                "comments": issue.comments,
                "html_url": issue.html_url
            })
            count += 1
        
        return f"Found {count} {state} issues in {owner}/{repo}:\n{json.dumps(issue_list, indent=2)}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: str, labels: Optional[List[str]] = None) -> str:
    """Create a new issue in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        title: Issue title
        body: Issue description
        labels: List of label names to apply (optional)
    """
    try:
        g = get_github_client()
        repository = g.get_repo(f"{owner}/{repo}")
        
        # Create the issue
        issue = repository.create_issue(
            title=title,
            body=body,
            labels=labels or []
        )
        
        return f"Successfully created issue #{issue.number} in {owner}/{repo}\nURL: {issue.html_url}"
        
    except GithubException as e:
        return f"GitHub API Error: {e.data.get('message', str(e))}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    try:
        # Check for GitHub token
        if not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
            print("❌ Error: GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set", file=sys.stderr)
            print("Get a token from: https://github.com/settings/tokens", file=sys.stderr)
            print("Then run: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here", file=sys.stderr)
            sys.exit(1)
            
        print(f"Starting GitHub MCP Server...", file=sys.stderr)
        print(f"GitHub user: {Github(os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']).get_user().login}", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}", file=sys.stderr)
        sys.exit(1)
