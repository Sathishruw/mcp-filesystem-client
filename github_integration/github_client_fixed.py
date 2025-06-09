#!/usr/bin/env python3

"""
Fixed GitHub MCP Client - Using the ACTUAL available tools
Based on real tool discovery from the GitHub MCP server
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


class FixedGitHubMCPClient:
    """
    Fixed GitHub MCP Client using the ACTUAL available tools from the server
    """
    
    def __init__(self, github_token: str, toolsets: Optional[List[str]] = None):
        """
        Initialize GitHub MCP Client with corrected tool names
        """
        self.github_token = github_token
        self.toolsets = toolsets or ['repos', 'issues', 'pull_requests']
        
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
        
        # Show actual available tools
        logger.info(f"✅ GitHub MCP Client ready!")
        logger.info(f"Available tools: {list(self.client.tools.keys())}")
    
    async def close(self):
        """Close the GitHub MCP client"""
        await self.client.close()
    
    # CORRECTED: User/Account Operations
    async def get_me(self) -> Dict[str, Any]:
        """Get information about the authenticated user - ACTUAL tool name"""
        return await self.client.call_tool("get_me")
    
    # CORRECTED: Repository Operations  
    async def search_repositories(self, query: str) -> Dict[str, Any]:
        """Search for repositories - ACTUAL tool name (not list_repositories)"""
        return await self.client.call_tool("search_repositories", {"query": query})
    
    async def get_my_repositories(self) -> Dict[str, Any]:
        """Get user's repositories by searching for them"""
        # Since there's no list_repositories, we search for user's repos
        me = await self.get_me()
        
        # Extract username from the 'me' response
        if isinstance(me.get('content'), list) and me['content']:
            # The response format might be different, let's handle it safely
            return await self.search_repositories(f"user:{me}")
        else:
            # Fallback: search without specific user
            return await self.search_repositories("user:Sathishruw")
    
    async def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new repository - ACTUAL tool name"""
        return await self.client.call_tool("create_repository", {
            "name": name,
            "description": description,
            "private": private
        })
    
    async def fork_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fork a repository - ACTUAL tool name"""
        return await self.client.call_tool("fork_repository", {
            "owner": owner,
            "repo": repo
        })
    
    # File Operations - CORRECTED tool names
    async def get_file_contents(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file contents - ACTUAL tool name"""
        return await self.client.call_tool("get_file_contents", {
            "owner": owner,
            "repo": repo,
            "path": path
        })
    
    async def create_or_update_file(self, owner: str, repo: str, path: str, 
                                  content: str, message: str) -> Dict[str, Any]:
        """Create or update a file - ACTUAL tool name"""
        return await self.client.call_tool("create_or_update_file", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": message
        })
    
    async def delete_file(self, owner: str, repo: str, path: str, message: str) -> Dict[str, Any]:
        """Delete a file - ACTUAL tool name"""
        return await self.client.call_tool("delete_file", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "message": message
        })
    
    # Branch Operations
    async def list_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """List branches in a repository - ACTUAL tool name"""
        return await self.client.call_tool("list_branches", {
            "owner": owner,
            "repo": repo
        })
    
    async def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> Dict[str, Any]:
        """Create a new branch - ACTUAL tool name"""
        return await self.client.call_tool("create_branch", {
            "owner": owner,
            "repo": repo,
            "branch_name": branch_name,
            "from_branch": from_branch
        })
    
    # Issue Management - CORRECTED
    async def list_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List issues in a repository - ACTUAL tool name"""
        return await self.client.call_tool("list_issues", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
    
    async def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get a specific issue - ACTUAL tool name"""
        return await self.client.call_tool("get_issue", {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number
        })
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict[str, Any]:
        """Create a new issue - ACTUAL tool name"""
        return await self.client.call_tool("create_issue", {
            "owner": owner,
            "repo": repo,
            "title": title,
            "body": body
        })
    
    async def update_issue(self, owner: str, repo: str, issue_number: int, 
                          title: Optional[str] = None, body: Optional[str] = None,
                          state: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing issue - ACTUAL tool name"""
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
    
    async def add_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """Add comment to an issue - ACTUAL tool name"""
        return await self.client.call_tool("add_issue_comment", {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
            "body": body
        })
    
    # Pull Request Management - CORRECTED
    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """List pull requests - ACTUAL tool name"""
        return await self.client.call_tool("list_pull_requests", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
    
    async def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get a specific pull request - ACTUAL tool name"""
        return await self.client.call_tool("get_pull_request", {
            "owner": owner,
            "repo": repo,
            "pull_number": pr_number
        })
    
    async def create_pull_request(self, owner: str, repo: str, title: str, 
                                head: str, base: str, body: str = "") -> Dict[str, Any]:
        """Create a new pull request - ACTUAL tool name"""
        return await self.client.call_tool("create_pull_request", {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
            "body": body
        })
    
    # Search Operations - CORRECTED
    async def search_code(self, query: str) -> Dict[str, Any]:
        """Search for code - ACTUAL tool name"""
        return await self.client.call_tool("search_code", {"query": query})
    
    async def search_issues(self, query: str) -> Dict[str, Any]:
        """Search for issues - ACTUAL tool name"""
        return await self.client.call_tool("search_issues", {"query": query})
    
    # Utility Methods
    async def get_available_tools(self) -> List[str]:
        """Get list of available GitHub tools"""
        return list(self.client.tools.keys())
    
    async def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        return self.client.tools.get(tool_name, {})


async def demo_fixed_github_client():
    """Demo function showing the CORRECTED GitHub MCP client"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
        return
    
    client = FixedGitHubMCPClient(github_token)
    
    try:
        await client.start()
        
        print("\n🔧 Available GitHub tools (ACTUAL):")
        tools = await client.get_available_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2d}. {tool}")
        
        print(f"\n👤 User information:")
        try:
            me = await client.get_me()
            print(f"✅ User info: {me}")
        except Exception as e:
            print(f"❌ Could not get user info: {e}")
        
        print(f"\n🔍 Searching for your repositories:")
        try:
            repos = await client.search_repositories("user:Sathishruw")
            print(f"✅ Repository search results: {repos}")
        except Exception as e:
            print(f"❌ Could not search repositories: {e}")
        
        print(f"\n📂 Searching for your mcp projects:")
        try:
            mcp_repos = await client.search_repositories("user:Sathishruw mcp")
            print(f"✅ MCP repository search: {mcp_repos}")
        except Exception as e:
            print(f"❌ Could not search MCP repositories: {e}")
        
        print(f"\n📄 Getting file from your repository:")
        try:
            readme = await client.get_file_contents("Sathishruw", "mcp-filesystem-client", "README.md")
            print(f"✅ README.md content type: {type(readme)}")
            if isinstance(readme.get('content'), list) and readme['content']:
                content_preview = str(readme['content'][0])[:200]
                print(f"Preview: {content_preview}...")
        except Exception as e:
            print(f"❌ Could not get file: {e}")
            
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def tool_discovery_mode():
    """Interactive tool discovery to understand what's actually available"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ Please set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
        return
    
    client = FixedGitHubMCPClient(github_token)
    
    try:
        await client.start()
        
        print(f"\n🔍 GitHub MCP Tool Discovery")
        print("=" * 50)
        
        tools = await client.get_available_tools()
        print(f"Total tools available: {len(tools)}")
        
        # Categorize tools
        categories = {
            "User/Account": [],
            "Repository": [],
            "File Operations": [],
            "Branch Operations": [],
            "Issue Management": [],
            "Pull Requests": [],
            "Search": [],
            "Code Security": [],
            "Other": []
        }
        
        for tool in tools:
            if "me" in tool:
                categories["User/Account"].append(tool)
            elif any(word in tool for word in ["repository", "repo", "fork"]):
                categories["Repository"].append(tool)
            elif any(word in tool for word in ["file", "push_files"]):
                categories["File Operations"].append(tool)
            elif "branch" in tool:
                categories["Branch Operations"].append(tool)
            elif "issue" in tool:
                categories["Issue Management"].append(tool)
            elif "pull_request" in tool:
                categories["Pull Requests"].append(tool)
            elif "search" in tool:
                categories["Search"].append(tool)
            elif any(word in tool for word in ["security", "scanning", "alert"]):
                categories["Code Security"].append(tool)
            else:
                categories["Other"].append(tool)
        
        # Print categorized tools
        for category, tool_list in categories.items():
            if tool_list:
                print(f"\n📋 {category}:")
                for tool in tool_list:
                    print(f"  - {tool}")
        
        print(f"\n💡 Key Insights:")
        print(f"  - No 'list_repositories' tool available")
        print(f"  - Use 'search_repositories' instead")
        print(f"  - 'get_me' provides user info")
        print(f"  - Rich file operations available")
        print(f"  - Complete issue/PR management")
        
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "discover":
        asyncio.run(tool_discovery_mode())
    else:
        asyncio.run(demo_fixed_github_client())
