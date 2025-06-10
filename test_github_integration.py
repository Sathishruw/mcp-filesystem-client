#!/usr/bin/env python3

import asyncio
import os
import json
from pathlib import Path
from fastmcp_client import FastMCPClient


async def test_github_server():
    """Test the GitHub MCP server."""
    print("\n=== Testing GitHub MCP Server ===\n")

    # Make sure we have the token
    if not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
        print("❌ Error: GITHUB_PERSONAL_ACCESS_TOKEN not set")
        print("Get a token from: https://github.com/settings/tokens")
        print("Run: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here")
        return

    # Start the GitHub server
    github_client = FastMCPClient(["python3", "github_server.py"])
    
    try:
        await github_client.start()
        await github_client.initialize()
        
        # Access available tools from the tools attribute
        print("Available GitHub tools:")
        for tool_name, tool_info in github_client.tools.items():
            print(f"  - {tool_name}: {tool_info.get('description', 'No description')}")
        print()
        
        # Test 1: List repositories
        print("1. Listing repositories...")
        result = await github_client.call_tool("list_repositories", {})
        print(f"Result: {result['content'][0]['text'][:200]}...")
        print()
        
        # Test 2: Search code (example search)
        print("2. Searching for Python files...")
        result = await github_client.call_tool("search_code", {
            "query": "language:python extension:py"
        })
        print(f"Result: {result['content'][0]['text'][:200]}...")
        print()
        
        print("✅ GitHub server tests completed!")
        
    except Exception as e:
        print(f"❌ Error during GitHub tests: {e}")
    finally:
        await github_client.close()


async def test_unified_server():
    """Test the unified filesystem + GitHub server."""
    print("\n=== Testing Unified MCP Server ===\n")
    
    # Start the unified server
    unified_client = FastMCPClient(["python3", "unified_server.py"])
    
    try:
        await unified_client.start()
        await unified_client.initialize()
        
        # Access available tools from the tools attribute
        print("Available tools in unified server:")
        tools = unified_client.tools
        filesystem_tools = [name for name in tools if not name.startswith('gh_')]
        github_tools = [name for name in tools if name.startswith('gh_')]
        unified_tools = [name for name in tools if name.startswith('sync_')]
        
        print(f"\nFilesystem tools ({len(filesystem_tools)}):")
        for tool_name in filesystem_tools:
            print(f"  - {tool_name}")
            
        print(f"\nGitHub tools ({len(github_tools)}):")
        for tool_name in github_tools:
            print(f"  - {tool_name}")
            
        print(f"\nUnified tools ({len(unified_tools)}):")
        for tool_name in unified_tools:
            print(f"  - {tool_name}")
        print()
        
        # Test 1: Create a local file
        print("1. Creating a local test file...")
        test_content = "# Test File\n\nThis is a test file created by the unified MCP server."
        result = await unified_client.call_tool("write_file", {
            "filepath": "test_unified.md",
            "content": test_content
        })
        print(f"Result: {result['content'][0]['text']}")
        
        # Test 2: List local files
        print("\n2. Listing local files...")
        result = await unified_client.call_tool("list_files", {})
        files = json.loads(result['content'][0]['text'].split('\n', 1)[1])
        print(f"Found {len(files)} files/directories")
        
        # Test 3: GitHub operation (if token is set)
        if os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
            print("\n3. Testing GitHub integration...")
            result = await unified_client.call_tool("gh_list_repositories", {})
            print(f"Result: {result['content'][0]['text'][:200]}...")
        else:
            print("\n3. Skipping GitHub tests (no token set)")
        
        print("\n✅ Unified server tests completed!")
        
    except Exception as e:
        print(f"❌ Error during unified tests: {e}")
    finally:
        await unified_client.close()


async def demo_sync_workflow():
    """Demonstrate syncing between GitHub and local filesystem."""
    print("\n=== Demo: GitHub <-> Local Sync Workflow ===\n")
    
    if not os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN"):
        print("❌ This demo requires GITHUB_PERSONAL_ACCESS_TOKEN")
        return
    
    print("This demonstrates how to sync files between GitHub and your local filesystem.")
    print("Note: You'll need to update the owner/repo values to use your own repository.\n")
    
    # Example code showing how sync would work
    example_code = '''
# Example: Download README from GitHub to local
result = await client.call_tool("sync_github_to_local", {
    "owner": "your-username",
    "repo": "your-repo",
    "github_path": "README.md",
    "local_path": "downloaded_readme.md"
})

# Example: Upload local file to GitHub
result = await client.call_tool("sync_local_to_github", {
    "local_path": "my_script.py",
    "owner": "your-username",
    "repo": "your-repo",
    "github_path": "scripts/my_script.py",
    "message": "Add new script via MCP"
})
'''
    
    print(example_code)


async def main():
    """Run all tests."""
    print("🚀 MCP GitHub Integration Test Suite")
    print("=" * 50)
    
    # Test individual servers
    await test_github_server()
    # await test_unified_server()
    
    # Show sync workflow demo
    await demo_sync_workflow()
    
    print("\n✨ All tests completed!")
    print("\nNext steps:")
    print("1. Set your GitHub token: export GITHUB_PERSONAL_ACCESS_TOKEN=your_token")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run servers individually:")
    print("   - python filesystem_server.py  (filesystem only)")
    print("   - python github_server.py      (GitHub only)")
    print("   - python unified_server.py     (both + sync tools)")


if __name__ == "__main__":
    asyncio.run(main())
