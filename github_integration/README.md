# 🚀 GitHub MCP Integration for your Filesystem Client

This integration extends your existing **mcp-filesystem-client** project to work with GitHub repositories using the official GitHub MCP server.

## 📦 What's Included

```
github_integration/
├── github_client.py        # GitHub-specific MCP client
├── unified_client.py       # Combined filesystem + GitHub client  
├── examples.py             # Practical workflow examples
├── setup.sh               # Automated setup script
├── requirements.txt       # Python dependencies
├── GITHUB_INTEGRATION.md  # Detailed documentation
└── README.md             # This file
```

## ⚡ Quick Start

### 1. Run Setup
```bash
cd github_integration
chmod +x setup.sh
./setup.sh
```

### 2. Set GitHub Token
```bash
# Get token from: https://github.com/settings/tokens
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### 3. Test Integration
```bash
# Test GitHub client
python github_client.py

# Test unified client (filesystem + GitHub)
python unified_client.py

# Interactive mode
python unified_client.py interactive

# Run example workflows
python examples.py
```

## 🎯 Key Features

### GitHub Operations
- ✅ List and search repositories
- ✅ Read/write files in repositories  
- ✅ Manage issues and pull requests
- ✅ Search code across repositories
- ✅ Repository analysis and monitoring

### Unified Operations
- ✅ Download GitHub files to local filesystem
- ✅ Sync repositories with local directories
- ✅ Cross-platform file operations
- ✅ Hybrid workflows (GitHub + local)

### Example Workflows
- 📦 **Repository Backup** - Download important files locally
- 📊 **Issue Analysis** - Analyze and report on repository issues  
- 🔍 **Code Search** - Search code patterns and save results
- 📈 **Repository Monitoring** - Track repository activity

## 🔧 Usage Examples

### Basic GitHub Operations
```python
from github_client import GitHubMCPClient

client = GitHubMCPClient(github_token)
await client.start()

# List your repositories
repos = await client.list_repositories()

# Read a file from your repo
content = await client.get_file_contents("your-username", "repo-name", "README.md")

# Create an issue
issue = await client.create_issue("owner", "repo", "Bug Report", "Description")
```

### Unified Operations
```python
from unified_client import UnifiedMCPClient

client = UnifiedMCPClient(github_token)
await client.start()

# Download GitHub file to local filesystem
await client.sync_repo_to_local("owner", "repo", "local_backup", ["README.md"])

# Read both local and GitHub files
local_files = await client.fs_list_files(".")
github_repos = await client.gh_list_repos()
```

## 🛠️ Architecture

Your integration follows this architecture:

```
┌─────────────────┐    ┌─────────────────┐
│  Your FastMCP   │◄──►│ Filesystem      │
│     Client      │    │ Server (Local)  │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│  GitHub MCP     │◄──►│ Official GitHub │
│    Client       │    │ MCP Server      │
│   (Docker)      │    │   (Docker)      │
└─────────────────┘    └─────────────────┘
```

## 📚 Documentation

- **[GITHUB_INTEGRATION.md](GITHUB_INTEGRATION.md)** - Complete integration guide
- **[examples.py](examples.py)** - Practical workflow examples
- **[GitHub MCP Server Docs](https://github.com/github/github-mcp-server)** - Official server documentation

## 🔒 Security

- ✅ GitHub token stored in environment variables (not code)
- ✅ Filesystem operations restricted to working directory
- ✅ GitHub access limited to your token permissions
- ✅ Docker isolation for GitHub MCP server

## 🎨 Customization

The integration is designed to be easily customizable:

- **Toolsets**: Choose which GitHub tools to enable
- **Workflows**: Create custom automation workflows
- **Error Handling**: Add your own error handling logic
- **Local Storage**: Customize local file organization

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**: Start Docker Desktop
2. **GitHub token invalid**: Check token permissions and expiry
3. **Tool not found**: Verify correct toolset is enabled
4. **Network issues**: Check GitHub and Docker Hub connectivity

### Getting Help

1. Check error messages for specific details
2. Read the detailed documentation in `GITHUB_INTEGRATION.md`
3. Test with interactive mode for easier debugging
4. Review example workflows in `examples.py`

## 🚀 Next Steps

1. **Explore Examples**: Run `python examples.py` to see practical workflows
2. **Customize Workflows**: Modify examples for your specific needs
3. **Add Features**: Extend the clients with additional functionality
4. **Integration**: Integrate with your existing tools and scripts

## 📄 License

This integration follows the same license as your main project.

---

**Happy coding! 🎉** Your filesystem client now has GitHub superpowers!
