# MCP Filesystem & GitHub Server

A complete implementation of Model Context Protocol (MCP) servers for filesystem and GitHub operations, with a unified server that combines both.

## 🚀 Features

- **Filesystem Server**: Secure local file operations (read, write, list, create directories)
- **GitHub Server**: Full GitHub API integration (repos, files, issues, search)
- **Unified Server**: Combined filesystem + GitHub with sync capabilities
- **Async Operations**: High-performance concurrent operations
- **Security**: Sandboxed filesystem access, secure token handling
- **Type Safety**: Full type hints and parameter validation

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp-play/fileSystem

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

### GitHub Token (for GitHub features)
```bash
# Get a token from: https://github.com/settings/tokens
# Required scopes: repo, read:user
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

## 🏃 Quick Start

### Option 1: Filesystem Server Only
```bash
python filesystem_server.py
```

### Option 2: GitHub Server Only
```bash
python github_server.py
```

### Option 3: Unified Server (Recommended)
```bash
python unified_server.py
```

### Using the Client
```python
from fastmcp_client import FastMCPClient

# Connect to unified server
client = FastMCPClient(["python3", "unified_server.py"])
await client.start()
await client.initialize()

# Filesystem operations
await client.call_tool("write_file", {
    "filepath": "hello.txt",
    "content": "Hello, World!"
})

# GitHub operations
repos = await client.call_tool("gh_list_repositories", {})

# Sync operations
await client.call_tool("sync_github_to_local", {
    "owner": "octocat",
    "repo": "Hello-World",
    "github_path": "README.md",
    "local_path": "downloads/readme.md"
})
```

## 📚 Available Tools

### Filesystem Tools
- `list_files(directory)` - List files and directories
- `read_file(filepath)` - Read file contents
- `write_file(filepath, content)` - Write content to file
- `create_directory(directory)` - Create new directory
- `get_working_directory()` - Get working directory info

### GitHub Tools
- `gh_list_repositories(user?)` - List GitHub repositories
- `gh_read_file(owner, repo, path, branch?)` - Read file from GitHub
- `gh_list_files(owner, repo, path?, branch?)` - List files in GitHub repo
- `gh_create_or_update_file(owner, repo, path, content, message, branch?)` - Create/update file
- `gh_list_issues(owner, repo, state?)` - List repository issues
- `create_issue(owner, repo, title, body, labels?)` - Create new issue
- `search_code(query, user?, repo?)` - Search code on GitHub

### Sync Tools (Unified Server Only)
- `sync_github_to_local(owner, repo, github_path, local_path)` - Download from GitHub
- `sync_local_to_github(local_path, owner, repo, github_path, message, branch?)` - Upload to GitHub

## 📁 Project Structure

```
mcp-play/fileSystem/
├── filesystem_server.py      # Original filesystem MCP server
├── github_server.py          # GitHub MCP server
├── unified_server.py         # Combined server with sync tools
├── fastmcp_client.py         # MCP client implementation
├── integration_test.py       # Integration tests
├── test_github_integration.py # GitHub integration tests
├── requirements.txt          # Python dependencies
├── README.MD                 # Architecture documentation
├── GITHUB_MCP_SERVER.md      # GitHub server documentation
└── github_integration/       # Additional GitHub integration examples
```

## 🏗️ Architecture

The project uses the Model Context Protocol (MCP) for client-server communication:

```
Your Application
       ↓
FastMCPClient
       ↓ (JSON-RPC over stdio)
   MCP Server
   ├── Filesystem Operations → Local Files
   └── GitHub Operations → GitHub API
```

Key architectural decisions:
- **Subprocess Communication**: Uses stdio instead of network sockets
- **Async/Await**: Non-blocking operations for better performance
- **Security First**: Sandboxed filesystem access, no path traversal
- **Type Safety**: Full type hints for all operations

## 🧪 Testing

Run the test suites:

```bash
# Test filesystem operations
python integration_test.py

# Test GitHub integration
python test_github_integration.py
```

## 🔒 Security

1. **Filesystem Security**:
   - All operations restricted to working directory
   - Path traversal attacks prevented
   - Safe error handling for binary files

2. **GitHub Security**:
   - Token stored in environment variables
   - Never hardcode tokens
   - Use minimal required scopes

## 📖 Documentation

- [Architecture Overview](README.MD) - Detailed code architecture
- [GitHub MCP Server](GITHUB_MCP_SERVER.md) - GitHub server documentation
- [GitHub Integration Guide](github_integration/GITHUB_INTEGRATION.md) - Integration examples

## 🎯 Use Cases

- **AI Assistants**: Give AI tools safe file system access
- **Automation**: Sync between GitHub and local files
- **Backup**: Download GitHub repositories locally
- **Bulk Operations**: Update multiple repositories
- **Issue Management**: Export issues for analysis
- **Code Search**: Search across repositories

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/anthropics/fastmcp)
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub integration
- Implements the [Model Context Protocol](https://modelcontextprotocol.io/) standard
