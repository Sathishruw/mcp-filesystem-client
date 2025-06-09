#!/usr/bin/env python3

"""
FIXED Unified MCP Client - Works with both Filesystem and GitHub MCP servers
Updated to use the correct GitHub MCP tool names
"""

import asyncio
import os
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastmcp_client import FastMCPClient
from github_client_fixed import FixedGitHubMCPClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FixedUnifiedMCPClient:
    """
    FIXED Unified client that manages both filesystem and GitHub MCP servers
    Now uses the correct GitHub MCP tool names discovered from the actual server
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.filesystem_client = None
        self.github_client = None
        self.github_token = github_token
        
        # Define filesystem server command
        filesystem_server_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "filesystem_server.py"
        )
        self.filesystem_command = ["python3", filesystem_server_path]
    
    async def start(self, enable_filesystem: bool = True, enable_github: bool = True):
        """Start the MCP clients"""
        
        if enable_filesystem:
            logger.info("Starting Filesystem MCP Client...")
            self.filesystem_client = FastMCPClient(self.filesystem_command)
            await self.filesystem_client.start()
            await self.filesystem_client.initialize()
            logger.info(f"✅ Filesystem MCP ready! Tools: {list(self.filesystem_client.tools.keys())}")
        
        if enable_github and self.github_token:
            logger.info("Starting GitHub MCP Client...")
            self.github_client = FixedGitHubMCPClient(self.github_token)  # FIXED: Use correct client
            await self.github_client.start()
            logger.info(f"✅ GitHub MCP ready! Tools: {await self.github_client.get_available_tools()}")
        elif enable_github:
            logger.warning("⚠️  GitHub token not provided, GitHub MCP not started")
    
    async def close(self):
        """Close all MCP clients"""
        if self.filesystem_client:
            await self.filesystem_client.close()
        if self.github_client:
            await self.github_client.close()
    
    # Filesystem operations (unchanged)
    async def fs_list_files(self, directory: str = ".") -> Dict[str, Any]:
        """List files using filesystem MCP"""
        if not self.filesystem_client:
            raise Exception("Filesystem client not initialized")
        return await self.filesystem_client.call_tool("list_files", {"directory": directory})
    
    async def fs_read_file(self, filepath: str) -> Dict[str, Any]:
        """Read file using filesystem MCP"""
        if not self.filesystem_client:
            raise Exception("Filesystem client not initialized")
        return await self.filesystem_client.call_tool("read_file", {"filepath": filepath})
    
    async def fs_write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write file using filesystem MCP"""
        if not self.filesystem_client:
            raise Exception("Filesystem client not initialized")
        return await self.filesystem_client.call_tool("write_file", {
            "filepath": filepath,
            "content": content
        })
    
    # FIXED GitHub operations using correct tool names
    async def gh_get_me(self) -> Dict[str, Any]:
        """Get authenticated user info"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.get_me()
    
    async def gh_search_repos(self, query: str = "user:Sathishruw") -> Dict[str, Any]:
        """Search GitHub repositories (FIXED: no list_repositories)"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.search_repositories(query)
    
    async def gh_get_my_repos(self) -> Dict[str, Any]:
        """Get user's repositories using search (FIXED method)"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.get_my_repositories()
    
    async def gh_get_file(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file from GitHub repository"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.get_file_contents(owner, repo, path)
    
    async def gh_list_issues(self, owner: str, repo: str) -> Dict[str, Any]:
        """List issues in GitHub repository"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.list_issues(owner, repo)
    
    async def gh_list_branches(self, owner: str, repo: str) -> Dict[str, Any]:
        """List branches in GitHub repository"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.list_branches(owner, repo)
    
    # Hybrid operations (updated for correct GitHub tools)
    async def sync_repo_to_local(self, owner: str, repo: str, local_dir: str, files: List[str]):
        """
        Download files from GitHub repo to local filesystem
        FIXED: Simplified since no list_directory_contents tool available
        """
        if not self.github_client or not self.filesystem_client:
            raise Exception("Both GitHub and Filesystem clients must be initialized")
        
        # Create local directory
        await self.filesystem_client.call_tool("create_directory", {"directory": local_dir})
        
        # Download each specified file
        for file_path in files:
            try:
                logger.info(f"Downloading {file_path}...")
                file_content = await self.github_client.get_file_contents(owner, repo, file_path)
                
                # Extract content (GitHub MCP returns structured response)
                if isinstance(file_content.get('content'), list):
                    for content_item in file_content['content']:
                        if content_item.get('type') == 'text':
                            content = content_item.get('text', '')
                            
                            # Save to local filesystem
                            local_path = f"{local_dir}/{file_path}"
                            await self.filesystem_client.call_tool("write_file", {
                                "filepath": local_path,
                                "content": content
                            })
                            logger.info(f"✅ Saved {file_path} to {local_path}")
                            break
                elif isinstance(file_content, str):
                    # Direct string response
                    local_path = f"{local_dir}/{file_path}"
                    await self.filesystem_client.call_tool("write_file", {
                        "filepath": local_path,
                        "content": file_content
                    })
                    logger.info(f"✅ Saved {file_path} to {local_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to download {file_path}: {e}")
    
    async def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from both clients"""
        tools = {}
        
        if self.filesystem_client:
            tools['filesystem'] = list(self.filesystem_client.tools.keys())
        
        if self.github_client:
            tools['github'] = await self.github_client.get_available_tools()
        
        return tools


async def demo_fixed_unified_client():
    """Demo the FIXED unified MCP client"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    client = FixedUnifiedMCPClient(github_token)
    
    try:
        # Start both clients
        await client.start(enable_filesystem=True, enable_github=bool(github_token))
        
        print("\n🔧 All available tools (ACTUAL):")
        all_tools = await client.get_all_tools()
        for service, tools in all_tools.items():
            print(f"  {service} ({len(tools)} tools):")
            for tool in tools:
                print(f"    - {tool}")
        
        print("\n📁 Local files:")
        local_files = await client.fs_list_files(".")
        print(local_files)
        
        if github_token:
            print("\n👤 GitHub user info:")
            try:
                me = await client.gh_get_me()
                print(f"✅ User info: {me}")
            except Exception as e:
                print(f"❌ Could not get user info: {e}")
            
            print("\n📚 Your GitHub repositories (using search):")
            try:
                repos = await client.gh_search_repos("user:Sathishruw")
                print(f"✅ Repository search: {repos}")
            except Exception as e:
                print(f"❌ Could not search repositories: {e}")
            
            # Example hybrid operation
            print(f"\n🔄 Hybrid operation example:")
            print(f"Downloading README.md from your mcp-filesystem-client to local")
            try:
                await client.sync_repo_to_local(
                    "Sathishruw", 
                    "mcp-filesystem-client", 
                    "downloaded_fixed", 
                    ["README.md"]
                )
                
                # Read the downloaded file locally
                local_readme = await client.fs_read_file("downloaded_fixed/README.md")
                print(f"📄 Downloaded README.md content type: {type(local_readme)}")
                
            except Exception as e:
                print(f"❌ Hybrid operation failed: {e}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def interactive_fixed_mode():
    """Interactive mode with FIXED GitHub tools"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    client = FixedUnifiedMCPClient(github_token)
    
    try:
        await client.start(enable_filesystem=True, enable_github=bool(github_token))
        
        print(f"\n🎉 FIXED Unified MCP Client Ready!")
        all_tools = await client.get_all_tools()
        for service, tools in all_tools.items():
            print(f"  {service}: {len(tools)} tools available")
        print(f"\nType 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\nfixed-unified> ").strip()
                
                if command == 'quit':
                    break
                elif command == 'help':
                    print("Available commands (CORRECTED):")
                    print("  Local filesystem:")
                    print("    fs-list [dir]           - List local files")
                    print("    fs-read <file>          - Read local file")
                    print("    fs-write <file>         - Write local file")
                    print("  GitHub (ACTUAL tools):")
                    print("    gh-me                   - Get user info")
                    print("    gh-search <query>       - Search repositories")
                    print("    gh-repos                - Get your repositories")
                    print("    gh-file <owner> <repo> <path> - Get file contents")
                    print("    gh-issues <owner> <repo> - List issues")
                    print("    gh-branches <owner> <repo> - List branches")
                    print("  Hybrid:")
                    print("    sync <owner> <repo> <localdir> <file> - Download file to local")
                    print("    tools                   - Show all available tools")
                    print("    quit                    - Exit")
                
                elif command == 'tools':
                    all_tools = await client.get_all_tools()
                    for service, tools in all_tools.items():
                        print(f"\n  {service.upper()} TOOLS:")
                        for i, tool in enumerate(tools, 1):
                            print(f"    {i:2d}. {tool}")
                
                elif command.startswith('fs-list'):
                    parts = command.split()
                    directory = parts[1] if len(parts) > 1 else "."
                    result = await client.fs_list_files(directory)
                    print(result)
                
                elif command.startswith('fs-read '):
                    filepath = command[8:]
                    result = await client.fs_read_file(filepath)
                    print(result)
                
                elif command == 'gh-me':
                    if client.github_client:
                        result = await client.gh_get_me()
                        print(result)
                    else:
                        print("GitHub client not available")
                
                elif command.startswith('gh-search '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    query = command[10:]  # Remove 'gh-search '
                    result = await client.gh_search_repos(query)
                    print(result)
                
                elif command == 'gh-repos':
                    if client.github_client:
                        result = await client.gh_get_my_repos()
                        print(result)
                    else:
                        print("GitHub client not available")
                
                elif command.startswith('gh-file '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 4:
                        print("Usage: gh-file <owner> <repo> <path>")
                        continue
                    owner, repo, path = parts[1], parts[2], parts[3]
                    result = await client.gh_get_file(owner, repo, path)
                    print(result)
                
                elif command.startswith('gh-issues '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: gh-issues <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.gh_list_issues(owner, repo)
                    print(result)
                
                elif command.startswith('gh-branches '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: gh-branches <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.gh_list_branches(owner, repo)
                    print(result)
                
                elif command.startswith('sync '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 5:
                        print("Usage: sync <owner> <repo> <localdir> <file>")
                        continue
                    owner, repo, localdir, file = parts[1], parts[2], parts[3], parts[4]
                    await client.sync_repo_to_local(owner, repo, localdir, [file])
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        logger.error(f"Failed to start fixed unified client: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_fixed_mode())
    else:
        asyncio.run(demo_fixed_unified_client())
