#!/usr/bin/env python3

"""
Alternative GitHub MCP Integration Approaches
Showing multiple ways to integrate without Docker
"""

import asyncio
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastmcp_client import FastMCPClient

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NativeGitHubMCPClient:
    """
    Alternative 1: Use the native Go binary (no Docker)
    """
    
    def __init__(self, github_token: str, binary_path: Optional[str] = None):
        self.github_token = github_token
        self.binary_path = binary_path or self._download_binary()
        
        # Build command for native binary
        self.server_command = [
            self.binary_path,
            "stdio"  # Use stdio communication
        ]
        
        # Set environment
        self.env = {
            **os.environ,
            "GITHUB_PERSONAL_ACCESS_TOKEN": github_token
        }
        
        # Initialize FastMCP client
        self.client = FastMCPClient(self.server_command)
    
    def _download_binary(self) -> str:
        """Download the GitHub MCP server binary"""
        # This is simplified - in reality you'd:
        # 1. Detect OS/architecture
        # 2. Download from GitHub releases
        # 3. Make executable
        # 4. Cache locally
        
        print("📦 Downloading GitHub MCP server binary...")
        
        # For demo purposes, assume binary exists
        binary_path = "/usr/local/bin/github-mcp-server"
        if not Path(binary_path).exists():
            raise Exception(f"""
            GitHub MCP server binary not found at {binary_path}
            
            To install:
            1. Download from: https://github.com/github/github-mcp-server/releases
            2. Extract and place in /usr/local/bin/
            3. Make executable: chmod +x /usr/local/bin/github-mcp-server
            
            Or build from source:
            git clone https://github.com/github/github-mcp-server
            cd github-mcp-server
            go build -o github-mcp-server cmd/github-mcp-server/main.go
            """)
        
        return binary_path
    
    async def start(self):
        """Start the native GitHub MCP client"""
        logger.info("Starting native GitHub MCP server...")
        
        # Modify the client to use custom environment
        original_start = self.client.start
        
        async def start_with_env():
            # Start process with custom environment
            self.client.process = await asyncio.create_subprocess_exec(
                *self.client.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env
            )
            
            # Start background tasks
            asyncio.create_task(self.client._read_stdout())
            asyncio.create_task(self.client._read_stderr())
            await asyncio.sleep(0.5)
        
        self.client.start = start_with_env
        
        await self.client.start()
        await self.client.initialize()
        logger.info("✅ Native GitHub MCP client ready!")


class EmbeddedGitHubClient:
    """
    Alternative 2: Embed GitHub API calls directly (no separate MCP server)
    """
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def start(self):
        """Initialize the embedded client"""
        logger.info("✅ Embedded GitHub client ready!")
    
    async def close(self):
        """Close the embedded client"""
        pass
    
    async def list_repositories(self) -> Dict[str, Any]:
        """List user repositories using direct API calls"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/user/repos",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    repos = await response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Found {len(repos)} repositories:\n" + 
                                       "\n".join([f"- {repo['name']}: {repo['description'] or 'No description'}" 
                                                for repo in repos[:10]])
                            }
                        ],
                        "isError": False
                    }
                else:
                    return {
                        "content": [{"type": "text", "text": f"Error: {response.status}"}],
                        "isError": True
                    }
    
    async def get_file_contents(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file contents using direct API"""
        import aiohttp
        import base64
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("encoding") == "base64":
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        return {
                            "content": [{"type": "text", "text": content}],
                            "isError": False
                        }
                else:
                    return {
                        "content": [{"type": "text", "text": f"Error: {response.status}"}],
                        "isError": True
                    }


class HybridGitHubClient:
    """
    Alternative 3: Hybrid approach - Use GitHub CLI + Python wrapper
    """
    
    def __init__(self):
        self._check_gh_cli()
    
    def _check_gh_cli(self):
        """Check if GitHub CLI is installed and authenticated"""
        try:
            result = subprocess.run(["gh", "auth", "status"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("GitHub CLI not authenticated. Run: gh auth login")
            logger.info("✅ GitHub CLI authenticated")
        except FileNotFoundError:
            raise Exception("GitHub CLI not installed. Install from: https://cli.github.com/")
    
    async def start(self):
        """Initialize hybrid client"""
        logger.info("✅ Hybrid GitHub client ready!")
    
    async def close(self):
        """Close hybrid client"""
        pass
    
    async def _run_gh_command(self, command: List[str]) -> str:
        """Run GitHub CLI command"""
        try:
            result = subprocess.run(
                ["gh"] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"GitHub CLI error: {e.stderr}")
    
    async def list_repositories(self) -> Dict[str, Any]:
        """List repositories using GitHub CLI"""
        try:
            output = await self._run_gh_command([
                "repo", "list", "--json", "name,description", "--limit", "10"
            ])
            
            return {
                "content": [{"type": "text", "text": f"Repositories:\n{output}"}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True
            }
    
    async def get_file_contents(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file contents using GitHub CLI"""
        try:
            output = await self._run_gh_command([
                "api", f"repos/{owner}/{repo}/contents/{path}",
                "--jq", ".content | @base64d"
            ])
            
            return {
                "content": [{"type": "text", "text": output}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True
            }


async def demo_alternatives():
    """Demo all alternative approaches"""
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    print("🔄 Testing Alternative GitHub Integration Approaches")
    print("=" * 60)
    
    # Alternative 1: Native Binary (commented out as it requires binary)
    print("\n1️⃣ Native Binary Approach (requires manual binary installation)")
    print("   - Download from GitHub releases")
    print("   - No Docker dependency")
    print("   - Direct process execution")
    
    # Alternative 2: Embedded API calls
    print("\n2️⃣ Embedded API Approach")
    if github_token:
        try:
            embedded = EmbeddedGitHubClient(github_token)
            await embedded.start()
            
            repos = await embedded.list_repositories()
            print(f"✅ Embedded approach works: {repos}")
            
        except Exception as e:
            print(f"❌ Embedded approach failed: {e}")
    else:
        print("❌ Needs GITHUB_PERSONAL_ACCESS_TOKEN")
    
    # Alternative 3: GitHub CLI
    print("\n3️⃣ GitHub CLI Approach")
    try:
        hybrid = HybridGitHubClient()
        await hybrid.start()
        
        repos = await hybrid.list_repositories()
        print(f"✅ GitHub CLI approach works: {repos}")
        
    except Exception as e:
        print(f"❌ GitHub CLI approach failed: {e}")
    
    print("\n📊 Comparison Summary:")
    print("Docker:     ✅ Easy setup  ✅ Isolation  ❌ Docker dependency")
    print("Native:     ✅ No Docker  ✅ Fast       ❌ Manual installation")
    print("Embedded:   ✅ Simple     ✅ Direct     ❌ Limited features")
    print("CLI:        ✅ Familiar   ✅ Full API   ❌ Requires 'gh' install")


if __name__ == "__main__":
    asyncio.run(demo_alternatives())
