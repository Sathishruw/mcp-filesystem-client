#!/usr/bin/env python3

"""
GitHub MCP Client - Integration with GitHub's official MCP server
This client extends your existing FastMCPClient to work with GitHub repositories
"""

import asyncio
import os
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path to import our FastMCPClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastmcp_client import FastMCPClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubMCPClient:
    """
    GitHub MCP Client that wraps the official GitHub MCP server
    """
    
    def __init__(self, github_token: str, toolsets: Optional[List[str]] = None):
        """
        Initialize GitHub MCP Client
        
        Args:
            github_token: Your GitHub Personal Access Token
            toolsets: List of toolsets to enable (e.g., ['repos', 'issues', 'pull_requests'])
                     If None, will enable common toolsets
        """
        self.github_token = github_token
        self.toolsets = toolsets or ['repos', 'issues', 'pull_requests', 'code_security']
        print(github_token)
        # Build the Docker command for GitHub MCP server
        self.server_command = [
            "docker", "run", "-i", "--rm",
            "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
            "-e", f"GITHUB_TOOLSETS={','.join(self.toolsets)}",
            "ghcr.io/github/github-mcp-server"
        ]
        
        # Initialize the FastMCP client with GitHub server command
        self.client = FastMCPClient(self.server_command)
    
    async def start(self):
        """Start the GitHub MCP client"""
        logger.info("Starting GitHub MCP Server...")
        await self.client.start()
        await self.client.initialize()
        logger.info(f"✅ GitHub MCP Client ready! Available tools: {list(self.client.tools.keys())}")
    
    async def close(self):
        """Close the GitHub MCP client"""
        await self.client.close()
    
    # Repository Management Tools
    async def list_repositories(self, owner: Optional[str] = None, type: str = "all") -> Dict[str, Any]:
        """
        List repositories for a user or organization
        
        Args:
            owner: GitHub username or organization (if None, lists your repos)
            type: Repository type ('all', 'owner', 'public', 'private', 'member')
        """
        args = {"type": type}
        if owner:
            args["owner"] = owner
        
        return await self.client.call_tool("list_repositories", args)
    
    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        return await self.client.call_tool("get_repository", {
            "owner": owner,
            "repo": repo
        })
    
    async def search_repositories(self, query: str, sort: str = "updated") -> Dict[str, Any]:
        """
        Search for repositories on GitHub
        
        Args:
            query: Search query
            sort: Sort order ('stars', 'forks', 'help-wanted-issues', 'updated')
        """
        return await self.client.call_tool("search_repositories", {
            "query": query,
            "sort": sort
        })
    
    # File Operations
    async def get_file_contents(self, owner: str, repo: str, path: str, ref: str = "main") -> Dict[str, Any]:
        """Get the contents of a file from a repository"""
        return await self.client.call_tool("get_file_contents", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": ref
        })
    
    async def create_or_update_file(self, owner: str, repo: str, path: str, 
                                  content: str, message: str, branch: str = "main") -> Dict[str, Any]:
        """Create or update a file in a repository"""
        return await self.client.call_tool("create_or_update_file", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": message,
            "branch": branch
        })
    
    async def list_directory_contents(self, owner: str, repo: str, path: str = "", ref: str = "main") -> Dict[str, Any]:
        """List contents of a directory in a repository"""
        return await self.client.call_tool("list_directory_contents", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": ref
        })
    
    # Issue Management
    async def list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List issues in a repository"""
        return await self.client.call_tool("list_issues", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
    
    async def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get a specific issue"""
        return await self.client.call_tool("get_issue", {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number
        })
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict[str, Any]:
        """Create a new issue"""
        return await self.client.call_tool("create_issue", {
            "owner": owner,
            "repo": repo,
            "title": title,
            "body": body
        })
    
    async def update_issue(self, owner: str, repo: str, issue_number: int, 
                          title: Optional[str] = None, body: Optional[str] = None,
                          state: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing issue"""
        args = {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number
        }
        if title:
            args["title"] = title
        if body:
            args["body"] = body
        if state:
            args["state"] = state
        
        return await self.client.call_tool("update_issue", args)
    
    # Pull Request Management
    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List pull requests in a repository"""
        return await self.client.call_tool("list_pull_requests", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
    
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get a specific pull request"""
        return await self.client.call_tool("get_pull_request", {
            "owner": owner,
            "repo": repo,
            "pull_number": pr_number
        })
    
    async def create_pull_request(self, owner: str, repo: str, title: str, 
                                head: str, base: str, body: str = "") -> Dict[str, Any]:
        """Create a new pull request"""
        return await self.client.call_tool("create_pull_request", {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
            "body": body
        })
    
    # Search Operations
    async def search_code(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
        """Search for code in repositories"""
        args = {"query": query}
        if owner and repo:
            args["query"] = f"{query} repo:{owner}/{repo}"
        
        return await self.client.call_tool("search_code", args)
    
    async def search_issues(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
        """Search for issues"""
        args = {"query": query}
        if owner and repo:
            args["query"] = f"{query} repo:{owner}/{repo}"
        
        return await self.client.call_tool("search_issues", args)
    
    # Utility Methods
    async def get_available_tools(self) -> List[str]:
        """Get list of available GitHub tools"""
        return list(self.client.tools.keys())
    
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        return self.client.tools.get(tool_name, {})


async def demo_github_client():
    """Demo function showing how to use the GitHub MCP client"""
    
    # You need to set your GitHub token
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
        print("You can get a token from: https://github.com/settings/tokens")
        return
    
    client = GitHubMCPClient(github_token)
    
    try:
        await client.start()
        
        print("\n🔧 Available GitHub tools:")
        tools = await client.get_available_tools()
        for tool in tools:
            print(f"  - {tool}")
        
        print("\n📁 Your repositories:")
        repos = await client.list_repositories()
        print(repos)
        
        # Example: Get repository info
        print(f"\n📖 Repository info for Sathishruw/mcp-filesystem-client:")
        try:
            repo_info = await client.get_repository("Sathishruw", "mcp-filesystem-client")
            print(repo_info)
        except Exception as e:
            print(f"Could not fetch repo info: {e}")
        
        # Example: List files in your repo
        print(f"\n📂 Files in your mcp-filesystem-client repository:")
        try:
            files = await client.list_directory_contents("Sathishruw", "mcp-filesystem-client")
            print(files)
        except Exception as e:
            print(f"Could not list files: {e}")
        
        # Example: Search your repositories
        print(f"\n🔍 Searching your repositories for 'mcp':")
        try:
            search_results = await client.search_repositories("user:Sathishruw mcp")
            print(search_results)
        except Exception as e:
            print(f"Could not search: {e}")
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def interactive_github_mode():
    """Interactive mode for GitHub operations"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
        print("You can get a token from: https://github.com/settings/tokens")
        return
    
    client = GitHubMCPClient(github_token)
    
    try:
        await client.start()
        
        print(f"\n🎉 Connected to GitHub MCP Server!")
        print(f"Available tools: {', '.join(await client.get_available_tools())}")
        print(f"\nType 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\ngithub> ").strip()
                
                if command == 'quit':
                    break
                elif command == 'help':
                    print("Available commands:")
                    print("  repos                    - List your repositories")
                    print("  repo <owner> <name>      - Get repository info")
                    print("  files <owner> <repo>     - List files in repository")
                    print("  file <owner> <repo> <path> - Get file contents")
                    print("  issues <owner> <repo>    - List issues")
                    print("  prs <owner> <repo>       - List pull requests")
                    print("  search-repos <query>     - Search repositories")
                    print("  search-code <query>      - Search code")
                    print("  tools                    - Show available tools")
                    print("  quit                     - Exit")
                
                elif command == 'tools':
                    tools = await client.get_available_tools()
                    for tool in tools:
                        info = await client.get_tool_info(tool)
                        print(f"  {tool}: {info.get('description', 'No description')}")
                
                elif command == 'repos':
                    result = await client.list_repositories()
                    print(result)
                
                elif command.startswith('repo '):
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: repo <owner> <name>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.get_repository(owner, repo)
                    print(result)
                
                elif command.startswith('files '):
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: files <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.list_directory_contents(owner, repo)
                    print(result)
                
                elif command.startswith('file '):
                    parts = command.split()
                    if len(parts) < 4:
                        print("Usage: file <owner> <repo> <path>")
                        continue
                    owner, repo, path = parts[1], parts[2], parts[3]
                    result = await client.get_file_contents(owner, repo, path)
                    print(result)
                
                elif command.startswith('issues '):
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: issues <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.list_issues(owner, repo)
                    print(result)
                
                elif command.startswith('prs '):
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: prs <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.list_pull_requests(owner, repo)
                    print(result)
                
                elif command.startswith('search-repos '):
                    query = command[13:]  # Remove 'search-repos '
                    result = await client.search_repositories(query)
                    print(result)
                
                elif command.startswith('search-code '):
                    query = command[12:]  # Remove 'search-code '
                    result = await client.search_code(query)
                    print(result)
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_github_mode())
    else:
        asyncio.run(demo_github_client())
