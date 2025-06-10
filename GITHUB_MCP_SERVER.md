# GitHub MCP Server Integration

This project now includes a GitHub MCP server that follows the same pattern as the filesystem server, providing GitHub operations through the Model Context Protocol.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set GitHub Token
```bash
# Get a token from: https://github.com/settings/tokens
# Required scopes: repo, read:user
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### 3. Run the Servers

You have three options:

#### Option A: Filesystem Server Only
```bash
python filesystem_server.py
```

#### Option B: GitHub Server Only
```bash
python github_server.py
```

#### Option C: Unified Server (Recommended)
```bash
python unified_server.py
```

## 📋 Available Servers

### 1. **filesystem_server.py** (Original)
Provides local file system operations:
- `list_files` - List files and directories
- `read_file` - Read file contents
- `write_file` - Write content to files
- `create_directory` - Create directories
- `get_working_directory` - Get working directory info

### 2. **github_server.py** (New)
Provides GitHub operations:
- `list_repositories` - List GitHub repositories
- `get_repository_info` - Get detailed repo information
- `read_github_file` - Read files from GitHub repos
- `list_github_files` - List files in GitHub repos
- `create_or_update_file` - Create/update files in repos
- `search_code` - Search code across GitHub
- `list_issues` - List repository issues
- `create_issue` - Create new issues

### 3. **unified_server.py** (New)
Combines both servers and adds sync capabilities:
- All filesystem tools (same as above)
- All GitHub tools (prefixed with `gh_`)
- `sync_github_to_local` - Download files from GitHub
- `sync_local_to_github` - Upload files to GitHub

## 🔧 Usage Examples

### Using with FastMCPClient

```python
from fastmcp_client import FastMCPClient

# For GitHub operations
client = FastMCPClient(["python3", "github_server.py"])
await client.start()
await client.initialize()

# List your repositories
result = await client.call_tool("list_repositories", {})

# Read a file from GitHub
result = await client.call_tool("read_github_file", {
    "owner": "octocat",
    "repo": "Hello-World",
    "path": "README.md"
})

# Create an issue
result = await client.call_tool("create_issue", {
    "owner": "your-username",
    "repo": "your-repo",
    "title": "Bug: Something is broken",
    "body": "Description of the issue..."
})
```

### Using the Unified Server

```python
# Start unified server
client = FastMCPClient(["python3", "unified_server.py"])
await client.start()

# Local file operations
await client.call_tool("write_file", {
    "filepath": "local_file.txt",
    "content": "Hello from local!"
})

# GitHub operations
await client.call_tool("gh_list_repositories", {})

# Sync operations
await client.call_tool("sync_github_to_local", {
    "owner": "octocat",
    "repo": "Hello-World",
    "github_path": "README.md",
    "local_path": "downloaded_readme.md"
})
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Your App      │
└────────┬────────┘
         │
┌────────▼────────┐
│ FastMCPClient   │
└────────┬────────┘
         │ JSON-RPC over stdio
         │
┌────────▼────────────────────────┐
│   MCP Servers                   │
├─────────────────┬───────────────┤
│ Filesystem      │    GitHub     │
│  Operations     │  Operations   │
└─────────────────┴───────────────┘
         │                │
         ▼                ▼
   Local Files      GitHub API
```

## 🔒 Security

1. **Filesystem Security**:
   - All operations restricted to working directory
   - Path traversal attacks prevented
   - No access outside sandbox

2. **GitHub Security**:
   - Token stored in environment variable
   - Never commit tokens to code
   - Use minimal required scopes

## 🧪 Testing

Run the test suite:
```bash
python test_github_integration.py
```

This will test:
- GitHub server functionality
- Unified server functionality
- Sync operations between GitHub and local

## 📝 Common Workflows

### 1. Backup GitHub Repository
```python
# List files in repo
files = await client.call_tool("gh_list_files", {
    "owner": "your-username",
    "repo": "important-repo"
})

# Download important files
for file in important_files:
    await client.call_tool("sync_github_to_local", {
        "owner": "your-username",
        "repo": "important-repo",
        "github_path": file["path"],
        "local_path": f"backup/{file['path']}"
    })
```

### 2. Bulk Update Files
```python
# Read local template
template = await client.call_tool("read_file", {
    "filepath": "template.md"
})

# Update multiple repos
for repo in repositories:
    await client.call_tool("gh_create_or_update_file", {
        "owner": "your-org",
        "repo": repo,
        "path": "CONTRIBUTING.md",
        "content": template,
        "message": "Add contributing guidelines"
    })
```

### 3. Issue Management
```python
# Get all open issues
issues = await client.call_tool("gh_list_issues", {
    "owner": "your-username",
    "repo": "your-repo",
    "state": "open"
})

# Save report locally
await client.call_tool("write_file", {
    "filepath": "issue_report.json",
    "content": json.dumps(issues, indent=2)
})
```

## 🚨 Troubleshooting

### "PyGithub not installed"
```bash
pip install PyGithub
```

### "GITHUB_PERSONAL_ACCESS_TOKEN not set"
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
```

### "API rate limit exceeded"
- Use authenticated requests (with token)
- Implement caching for repeated requests
- Consider GitHub Apps for higher limits

### "Access denied" errors
- Check token has required scopes
- Verify repository permissions
- Ensure file paths are correct

## 🔮 Future Enhancements

Potential additions:
- GitHub Actions integration
- Webhook support
- Gist management
- Organization management
- Advanced search capabilities
- Caching layer for API calls
- Batch operations
- Progress callbacks for large operations

## 📄 License

This integration follows the same license as the main project.
