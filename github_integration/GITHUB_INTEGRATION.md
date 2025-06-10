# GitHub MCP Integration

This directory contains the integration between your existing MCP filesystem client and GitHub's official MCP server.

## 🏗️ Architecture

```
Your FastMCPClient ←→ [Filesystem Server] (Local files)
                  ←→ [GitHub MCP Server] (GitHub API via Docker)
```

## 📁 Files Overview

- **`github_client.py`** - GitHub-specific MCP client wrapper
- **`unified_client.py`** - Unified client that manages both filesystem and GitHub
- **`setup.sh`** - Setup script for dependencies and Docker image
- **`examples.py`** - Practical examples and workflows
- **`GITHUB_INTEGRATION.md`** - This documentation

## 🚀 Quick Start

### 1. Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (downloads Docker image, checks dependencies)
./setup.sh
```

### 2. Get GitHub Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Create a new **Personal Access Token (classic)** with these permissions:
   - `repo` (Full control of private repositories)
   - `read:user` (Read user profile data)
   - `read:org` (Read organization data)
3. Export the token:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### 3. Test the Integration

```bash
# Test GitHub client only
python github_client.py

# Test unified client (filesystem + GitHub)
python unified_client.py

# Interactive mode
python unified_client.py interactive
```

## 🔧 Available GitHub Tools

The GitHub MCP server provides these tools (depending on enabled toolsets):

### Repository Management
- `list_repositories` - List user/org repositories
- `get_repository` - Get repository details
- `search_repositories` - Search for repositories
- `fork_repository` - Fork a repository

### File Operations
- `get_file_contents` - Read file from repository
- `create_or_update_file` - Create/update files
- `delete_file` - Delete files
- `list_directory_contents` - List directory contents

### Issue Management
- `list_issues` - List repository issues
- `get_issue` - Get specific issue
- `create_issue` - Create new issue
- `update_issue` - Update existing issue
- `add_issue_comment` - Add comment to issue

### Pull Request Management
- `list_pull_requests` - List pull requests
- `get_pull_request` - Get specific PR
- `create_pull_request` - Create new PR
- `update_pull_request` - Update existing PR
- `merge_pull_request` - Merge pull request

### Search Operations
- `search_code` - Search code across repositories
- `search_issues` - Search issues and PRs
- `search_commits` - Search commit history

## 💡 Usage Examples

### Basic GitHub Operations

```python
from github_client import GitHubMCPClient

client = GitHubMCPClient(github_token)
await client.start()

# List your repositories
repos = await client.list_repositories()

# Get file from repository
content = await client.get_file_contents("owner", "repo", "README.md")

# Create an issue
issue = await client.create_issue("owner", "repo", "Bug report", "Description here")
```

### Unified Operations (GitHub + Filesystem)

```python
from unified_client import UnifiedMCPClient

client = UnifiedMCPClient(github_token)
await client.start()

# Download GitHub file to local filesystem
await client.sync_repo_to_local("owner", "repo", "local_dir", ["README.md"])

# Read the local file
local_content = await client.fs_read_file("local_dir/README.md")

# List both local and GitHub files
local_files = await client.fs_list_files(".")
github_files = await client.gh_list_repos()
```

## 🔄 Common Workflows

### 1. Repository Analysis
```python
# Get repository info
repo_info = await github_client.get_repository("owner", "repo")

# List all files in the repository
files = await github_client.list_directory_contents("owner", "repo")

# Search for specific code patterns
search_results = await github_client.search_code("function main repo:owner/repo")
```

### 2. Issue Management
```python
# List open issues
issues = await github_client.list_issues("owner", "repo", state="open")

# Create a new issue
new_issue = await github_client.create_issue(
    "owner", "repo", 
    "Feature Request", 
    "Please add support for..."
)

# Add comment to existing issue
await github_client.add_issue_comment("owner", "repo", issue_number, "Thanks for reporting!")
```

### 3. Code Review Workflow
```python
# List open pull requests
prs = await github_client.list_pull_requests("owner", "repo")

# Get PR details
pr_details = await github_client.get_pull_request("owner", "repo", pr_number)

# Add review comment
await github_client.add_pull_request_review_comment(
    "owner", "repo", pr_number, 
    "This looks good!", 
    path="src/main.py", 
    line=42
)
```

### 4. Local-GitHub Sync
```python
# Download multiple files from GitHub
await unified_client.sync_repo_to_local(
    "owner", "repo", "local_backup", 
    ["README.md", "src/main.py", "requirements.txt"]
)

# Work on files locally
content = await unified_client.fs_read_file("local_backup/README.md")
modified_content = content + "\n\n## Updates\nNew section added locally"
await unified_client.fs_write_file("local_backup/README.md", modified_content)

# Note: Uploading back to GitHub requires additional implementation
```

## 🛠️ Customization

### Enable Different Toolsets

```python
# Enable specific GitHub toolsets
client = GitHubMCPClient(
    github_token, 
    toolsets=['repos', 'issues', 'pull_requests', 'code_security']
)

# Enable all available toolsets
client = GitHubMCPClient(github_token, toolsets=['all'])
```

### Error Handling

```python
try:
    result = await github_client.get_repository("owner", "nonexistent-repo")
except Exception as e:
    print(f"Repository not found: {e}")
```

## 🔍 Debugging

### Check Available Tools
```python
tools = await github_client.get_available_tools()
print("Available GitHub tools:", tools)

# Get tool details
tool_info = await github_client.get_tool_info("list_repositories")
print("Tool description:", tool_info.get('description'))
```

### View Docker Logs
```bash
# Run GitHub MCP server with verbose output
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN \
  -e GITHUB_TOOLSETS=repos,issues \
  ghcr.io/github/github-mcp-server
```

## 🚨 Security Considerations

1. **Token Permissions**: Only grant the minimum required permissions to your GitHub token
2. **Token Storage**: Never commit tokens to repositories; use environment variables
3. **Access Control**: The GitHub MCP server can only access repositories you have permission for
4. **Local Files**: The filesystem server is restricted to the working directory for security

## 📚 Additional Resources

- [GitHub MCP Server Documentation](https://github.com/github/github-mcp-server)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**: Ensure Docker Desktop is started
2. **Token permissions**: Verify your GitHub token has the required scopes
3. **Network issues**: Check if you can reach GitHub and Docker Hub
4. **Tool not found**: Ensure the toolset containing the tool is enabled

### Getting Help

If you encounter issues:

1. Check the error messages for specific details
2. Verify your GitHub token permissions
3. Test with the interactive mode for easier debugging
4. Review the official GitHub MCP server documentation
