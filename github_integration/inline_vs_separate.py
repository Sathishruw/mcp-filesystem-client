#!/usr/bin/env python3

"""
Comparison: Inline vs Separate Integration Approaches
This shows the difference between mixing GitHub features into your existing client
vs keeping them separate
"""

import asyncio
import os
from typing import Dict, Any, List, Optional

# === INLINE APPROACH (what I DIDN'T do) ===

class InlineFastMCPClient:
    """
    Example of what it would look like if I mixed GitHub into your existing client
    This violates separation of concerns and makes the code complex
    """
    
    def __init__(self, server_command: List[str], github_token: Optional[str] = None):
        # Original filesystem MCP client code
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        self.pending_requests = {}
        self.tools = {}
        
        # NEW: GitHub-specific additions mixed in
        self.github_token = github_token
        self.github_tools = {}
        self.github_process = None
        
        if github_token:
            # GitHub MCP server command mixed into constructor
            self.github_command = [
                "docker", "run", "-i", "--rm",
                "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
                "ghcr.io/github/github-mcp-server"
            ]
    
    async def start(self):
        """Start both filesystem and GitHub servers - mixed responsibilities"""
        # Original filesystem server startup
        await self._start_filesystem_server()
        
        # NEW: GitHub server startup mixed in
        if self.github_token:
            await self._start_github_server()
    
    async def _start_filesystem_server(self):
        """Original filesystem server logic"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # ... rest of filesystem setup
    
    async def _start_github_server(self):
        """NEW: GitHub server logic mixed into existing class"""
        self.github_process = await asyncio.create_subprocess_exec(
            *self.github_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # ... GitHub-specific setup
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None, service: str = "filesystem"):
        """Modified to handle both filesystem and GitHub tools - confusing interface"""
        
        if service == "filesystem":
            # Original filesystem tool call
            return await self._call_filesystem_tool(name, arguments)
        elif service == "github":
            # NEW: GitHub tool call mixed in
            return await self._call_github_tool(name, arguments)
        else:
            raise ValueError(f"Unknown service: {service}")
    
    async def _call_filesystem_tool(self, name: str, arguments: Dict[str, Any]):
        """Original filesystem tool calling logic"""
        # ... existing implementation
        pass
    
    async def _call_github_tool(self, name: str, arguments: Dict[str, Any]):
        """NEW: GitHub tool calling logic mixed into existing class"""
        # ... GitHub-specific implementation
        pass
    
    # PROBLEM: Interface becomes confusing
    async def list_files(self, directory: str = "."):
        """Original filesystem method"""
        return await self.call_tool("list_files", {"directory": directory}, service="filesystem")
    
    async def list_repos(self):
        """NEW: GitHub method mixed with filesystem methods"""
        return await self.call_tool("list_repositories", {}, service="github")
    
    async def close(self):
        """Close both servers - mixed cleanup logic"""
        if self.process:
            self.process.terminate()
        if self.github_process:
            self.github_process.terminate()


# === SEPARATE APPROACH (what I DID) ===

class CleanFastMCPClient:
    """
    Your original client - unchanged and focused on filesystem operations
    Single responsibility: MCP communication with filesystem server
    """
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        self.pending_requests = {}
        self.tools = {}
    
    async def start(self):
        """Start filesystem server - single responsibility"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # ... filesystem-specific setup only
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None):
        """Call filesystem tools - clear, focused interface"""
        # ... filesystem tool calling logic only
        pass
    
    async def list_files(self, directory: str = "."):
        """Filesystem-only operation"""
        return await self.call_tool("list_files", {"directory": directory})
    
    async def close(self):
        """Clean shutdown of filesystem server only"""
        if self.process:
            self.process.terminate()


class SeparateGitHubMCPClient:
    """
    Separate GitHub client - focused on GitHub operations only
    Single responsibility: MCP communication with GitHub server
    """
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.server_command = [
            "docker", "run", "-i", "--rm",
            "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={github_token}",
            "ghcr.io/github/github-mcp-server"
        ]
        self.client = CleanFastMCPClient(self.server_command)
    
    async def start(self):
        """Start GitHub server - single responsibility"""
        await self.client.start()
    
    async def list_repositories(self):
        """GitHub-only operation"""
        return await self.client.call_tool("list_repositories")
    
    async def close(self):
        """Clean shutdown of GitHub server only"""
        await self.client.close()


class ComposedUnifiedClient:
    """
    Unified client that COMPOSES separate clients rather than inheriting
    Clean composition pattern - each client handles its own responsibility
    """
    
    def __init__(self, github_token: Optional[str] = None):
        # Composition: each client is independent
        self.filesystem_client = None
        self.github_client = None
        
        if github_token:
            self.github_client = SeparateGitHubMCPClient(github_token)
    
    async def start(self, enable_filesystem: bool = True, enable_github: bool = True):
        """Start clients independently"""
        if enable_filesystem:
            filesystem_server_path = "filesystem_server.py"  # Your existing server
            self.filesystem_client = CleanFastMCPClient(["python3", filesystem_server_path])
            await self.filesystem_client.start()
        
        if enable_github and self.github_client:
            await self.github_client.start()
    
    # Clear, explicit method names - no confusion about which service
    async def fs_list_files(self, directory: str = "."):
        """Filesystem operation - explicit prefix"""
        if not self.filesystem_client:
            raise Exception("Filesystem client not initialized")
        return await self.filesystem_client.list_files(directory)
    
    async def gh_list_repos(self):
        """GitHub operation - explicit prefix"""
        if not self.github_client:
            raise Exception("GitHub client not initialized")
        return await self.github_client.list_repositories()
    
    async def close(self):
        """Clean shutdown - each client handles its own cleanup"""
        if self.filesystem_client:
            await self.filesystem_client.close()
        if self.github_client:
            await self.github_client.close()


async def demo_comparison():
    """Demonstrate the difference between approaches"""
    
    print("🔄 Comparing Integration Approaches")
    print("=" * 50)
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    print("\n❌ INLINE APPROACH PROBLEMS:")
    print("1. Mixed responsibilities in one class")
    print("2. Confusing interface (service parameter)")
    print("3. Complex constructor with optional GitHub")
    print("4. Hard to test filesystem without GitHub")
    print("5. GitHub bugs can break filesystem operations")
    print("6. Violates Single Responsibility Principle")
    
    print("\n✅ SEPARATE APPROACH BENEFITS:")
    print("1. Each client has single responsibility")
    print("2. Clear, explicit interfaces")
    print("3. Independent testing possible")
    print("4. Easy to add/remove features")
    print("5. Follows composition over inheritance")
    print("6. Professional software architecture")
    
    if github_token:
        print("\n🧪 Testing Separate Approach:")
        try:
            unified = ComposedUnifiedClient(github_token)
            await unified.start(enable_filesystem=False, enable_github=True)  # GitHub only
            
            repos = await unified.gh_list_repos()
            print(f"✅ GitHub works independently: {type(repos)}")
            
            await unified.close()
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📊 Code Quality Comparison:")
    print("Inline Approach:")
    print("  - Lines of code: ~200 (complex)")
    print("  - Responsibilities: 3+ (filesystem, GitHub, coordination)")
    print("  - Testing complexity: High (mocked dependencies)")
    print("  - Maintainability: Low (changes affect everything)")
    
    print("\nSeparate Approach:")
    print("  - Lines of code: ~150 total (3 focused classes)")
    print("  - Responsibilities: 1 each (clear boundaries)")
    print("  - Testing complexity: Low (independent units)")
    print("  - Maintainability: High (isolated changes)")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"Separate folder structure with composed clients provides:")
    print(f"✅ Better architecture")
    print(f"✅ Easier maintenance") 
    print(f"✅ Clearer interfaces")
    print(f"✅ Professional organization")


if __name__ == "__main__":
    asyncio.run(demo_comparison())
