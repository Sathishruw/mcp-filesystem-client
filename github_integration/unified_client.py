#!/usr/bin/env python3

"""
Unified MCP Client - Works with both Filesystem and GitHub MCP servers
This demonstrates how to orchestrate multiple MCP servers together
"""

import asyncio
import os
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastmcp_client import FastMCPClient
from github_client import GitHubMCPClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedMCPClient:
    """
    Unified client that manages both filesystem and GitHub MCP servers
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
            self.github_client = GitHubMCPClient(self.github_token)
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
    
    # Filesystem operations
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
    
    # GitHub operations
    async def gh_list_repos(self) -> Dict[str, Any]:
        """List GitHub repositories"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.list_repositories()
    
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
    
    # Hybrid operations (combining filesystem + GitHub)
    async def sync_repo_to_local(self, owner: str, repo: str, local_dir: str, files: List[str] = None):
        """
        Download files from GitHub repo to local filesystem
        
        Args:
            owner: GitHub repository owner
            repo: Repository name
            local_dir: Local directory to save files
            files: List of files to download (if None, will list and ask)
        """
        if not self.github_client or not self.filesystem_client:
            raise Exception("Both GitHub and Filesystem clients must be initialized")
        
        # Create local directory
        await self.filesystem_client.call_tool("create_directory", {"directory": local_dir})
        
        if not files:
            # List files in GitHub repo
            repo_files = await self.github_client.list_directory_contents(owner, repo)
            print(f"Files in {owner}/{repo}:")
            print(repo_files)
            return
        
        # Download each file
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
                
            except Exception as e:
                logger.error(f"❌ Failed to download {file_path}: {e}")
    
    async def commit_local_changes(self, owner: str, repo: str, local_dir: str, 
                                 commit_message: str, branch: str = "main"):
        """
        Upload local changes back to GitHub repository
        
        Args:
            owner: GitHub repository owner
            repo: Repository name
            local_dir: Local directory with changes
            commit_message: Commit message
            branch: Target branch
        """
        if not self.github_client or not self.filesystem_client:
            raise Exception("Both GitHub and Filesystem clients must be initialized")
        
        # List local files
        local_files = await self.filesystem_client.call_tool("list_files", {"directory": local_dir})
        print(f"Local files to commit: {local_files}")
        
        # This is a simplified version - in reality you'd want to:
        # 1. Compare with remote files
        # 2. Handle binary files
        # 3. Handle deletions
        # 4. Create proper commits
        
        logger.warning("⚠️  Commit functionality is simplified - implement proper git workflow for production")
    
    async def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from both clients"""
        tools = {}
        
        if self.filesystem_client:
            tools['filesystem'] = list(self.filesystem_client.tools.keys())
        
        if self.github_client:
            tools['github'] = await self.github_client.get_available_tools()
        
        return tools


async def demo_unified_client():
    """Demo the unified MCP client"""
    
    # Get GitHub token
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    client = UnifiedMCPClient(github_token)
    
    try:
        # Start both clients
        await client.start(enable_filesystem=True, enable_github=bool(github_token))
        
        print("\n🔧 All available tools:")
        all_tools = await client.get_all_tools()
        for service, tools in all_tools.items():
            print(f"  {service}: {', '.join(tools)}")
        
        print("\n📁 Local files:")
        local_files = await client.fs_list_files(".")
        print(local_files)
        
        if github_token:
            print("\n📚 Your GitHub repositories:")
            repos = await client.gh_list_repos()
            print(repos)
            
            # Example hybrid operation
            print(f"\n🔄 Hybrid operation example:")
            print(f"Let's download README.md from your mcp-filesystem-client to local")
            try:
                await client.sync_repo_to_local(
                    "Sathishruw", 
                    "mcp-filesystem-client", 
                    "downloaded", 
                    ["README.md"]
                )
                
                # Read the downloaded file locally
                local_readme = await client.fs_read_file("downloaded/README.md")
                print(f"📄 Downloaded README.md content preview:")
                if isinstance(local_readme, str) and len(local_readme) > 200:
                    print(local_readme[:200] + "...")
                else:
                    print(local_readme)
                    
            except Exception as e:
                print(f"Hybrid operation failed: {e}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def interactive_unified_mode():
    """Interactive mode for unified operations"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    client = UnifiedMCPClient(github_token)
    
    try:
        await client.start(enable_filesystem=True, enable_github=bool(github_token))
        
        print(f"\n🎉 Unified MCP Client Ready!")
        all_tools = await client.get_all_tools()
        for service, tools in all_tools.items():
            print(f"  {service}: {', '.join(tools)}")
        print(f"\nType 'help' for commands, 'quit' to exit")
        
        while True:
            try:
                command = input("\nunified> ").strip()
                
                if command == 'quit':
                    break
                elif command == 'help':
                    print("Available commands:")
                    print("  Local filesystem:")
                    print("    fs-list [dir]           - List local files")
                    print("    fs-read <file>          - Read local file")
                    print("    fs-write <file>         - Write local file (prompts for content)")
                    print("  GitHub:")
                    print("    gh-repos                - List your repositories")
                    print("    gh-files <owner> <repo> - List files in GitHub repo")
                    print("    gh-read <owner> <repo> <path> - Read GitHub file")
                    print("    gh-issues <owner> <repo> - List issues")
                    print("  Hybrid:")
                    print("    sync <owner> <repo> <localdir> <file> - Download GitHub file to local")
                    print("    tools                   - Show all available tools")
                    print("    quit                    - Exit")
                
                elif command == 'tools':
                    all_tools = await client.get_all_tools()
                    for service, tools in all_tools.items():
                        print(f"  {service}:")
                        for tool in tools:
                            print(f"    - {tool}")
                
                elif command.startswith('fs-list'):
                    parts = command.split()
                    directory = parts[1] if len(parts) > 1 else "."
                    result = await client.fs_list_files(directory)
                    print(result)
                
                elif command.startswith('fs-read '):
                    filepath = command[8:]  # Remove 'fs-read '
                    result = await client.fs_read_file(filepath)
                    print(result)
                
                elif command.startswith('fs-write '):
                    filepath = command[9:]  # Remove 'fs-write '
                    print("Enter content (Ctrl+D to finish):")
                    content = sys.stdin.read()
                    result = await client.fs_write_file(filepath, content)
                    print(result)
                
                elif command == 'gh-repos':
                    if client.github_client:
                        result = await client.gh_list_repos()
                        print(result)
                    else:
                        print("GitHub client not available")
                
                elif command.startswith('gh-files '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 3:
                        print("Usage: gh-files <owner> <repo>")
                        continue
                    owner, repo = parts[1], parts[2]
                    result = await client.github_client.list_directory_contents(owner, repo)
                    print(result)
                
                elif command.startswith('gh-read '):
                    if not client.github_client:
                        print("GitHub client not available")
                        continue
                    parts = command.split()
                    if len(parts) < 4:
                        print("Usage: gh-read <owner> <repo> <path>")
                        continue
                    owner, repo, path = parts[1], parts[2], parts[3]
                    result = await client.gh_get_file(owner, repo, path)
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
        logger.error(f"Failed to start unified client: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_unified_mode())
    else:
        asyncio.run(demo_unified_client())
