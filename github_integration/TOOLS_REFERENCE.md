# 🔧 GitHub MCP Tools: Expected vs Actual

## 🎯 **The Issue**

I initially assumed certain tool names based on common patterns, but the **actual GitHub MCP server** has different tool names. This is a great example of why **tool discovery** is important when working with MCP servers!

## ❌ **What I Expected (WRONG)**

```python
# These tools DON'T exist in the GitHub MCP server:
await client.call_tool("list_repositories")        # ❌ DOESN'T EXIST
await client.call_tool("list_directory_contents")  # ❌ DOESN'T EXIST  
await client.call_tool("get_repository")           # ❌ DOESN'T EXIST
```

## ✅ **What's Actually Available (CORRECT)**

Based on your error message, here are the **actual** available tools:

### **🔍 Search & Discovery**
```python
await client.call_tool("search_repositories", {"query": "user:Sathishruw"})
await client.call_tool("search_code", {"query": "async def"})  
await client.call_tool("search_issues", {"query": "bug"})
```

### **👤 User Information**
```python
await client.call_tool("get_me")  # Get authenticated user info
```

### **📁 Repository Management**
```python
await client.call_tool("create_repository", {"name": "new-repo"})
await client.call_tool("fork_repository", {"owner": "owner", "repo": "repo"})
```

### **📄 File Operations**
```python
await client.call_tool("get_file_contents", {"owner": "owner", "repo": "repo", "path": "README.md"})
await client.call_tool("create_or_update_file", {"owner": "owner", "repo": "repo", "path": "file.txt", "content": "content", "message": "commit msg"})
await client.call_tool("delete_file", {"owner": "owner", "repo": "repo", "path": "file.txt", "message": "delete msg"})
await client.call_tool("push_files", {...})
```

### **🌿 Branch Operations**
```python
await client.call_tool("list_branches", {"owner": "owner", "repo": "repo"})
await client.call_tool("create_branch", {"owner": "owner", "repo": "repo", "branch_name": "feature"})
await client.call_tool("list_tags", {"owner": "owner", "repo": "repo"})
await client.call_tool("get_tag", {"owner": "owner", "repo": "repo", "tag": "v1.0"})
```

### **🐛 Issue Management**
```python
await client.call_tool("list_issues", {"owner": "owner", "repo": "repo"})
await client.call_tool("get_issue", {"owner": "owner", "repo": "repo", "issue_number": 123})
await client.call_tool("create_issue", {"owner": "owner", "repo": "repo", "title": "Bug", "body": "Description"})
await client.call_tool("update_issue", {"owner": "owner", "repo": "repo", "issue_number": 123, "state": "closed"})
await client.call_tool("add_issue_comment", {"owner": "owner", "repo": "repo", "issue_number": 123, "body": "comment"})
```

### **🔄 Pull Request Management**
```python
await client.call_tool("list_pull_requests", {"owner": "owner", "repo": "repo"})
await client.call_tool("get_pull_request", {"owner": "owner", "repo": "repo", "pull_number": 456})
await client.call_tool("create_pull_request", {"owner": "owner", "repo": "repo", "title": "Feature", "head": "feature", "base": "main"})
await client.call_tool("update_pull_request", {"owner": "owner", "repo": "repo", "pull_number": 456})
await client.call_tool("merge_pull_request", {"owner": "owner", "repo": "repo", "pull_number": 456})
```

### **🔐 Security & Code Analysis**
```python
await client.call_tool("list_code_scanning_alerts", {"owner": "owner", "repo": "repo"})
await client.call_tool("get_code_scanning_alert", {"owner": "owner", "repo": "repo", "alert_number": 789})
```

### **🤖 GitHub Copilot Integration**
```python
await client.call_tool("assign_copilot_to_issue", {"owner": "owner", "repo": "repo", "issue_number": 123})
await client.call_tool("request_copilot_review", {"owner": "owner", "repo": "repo", "pull_number": 456})
```

## 📊 **Categorized Tool List**

Here are all **55 actual tools** categorized:

### **User/Account (1 tool)**
- `get_me`

### **Repository Management (3 tools)**  
- `create_repository`
- `fork_repository`
- `search_repositories`

### **File Operations (4 tools)**
- `get_file_contents`
- `create_or_update_file` 
- `delete_file`
- `push_files`

### **Branch/Tag Operations (5 tools)**
- `list_branches`
- `create_branch`
- `list_tags`
- `get_tag`
- `get_commit`

### **Issue Management (6 tools)**
- `list_issues`
- `get_issue`
- `create_issue`
- `update_issue`
- `add_issue_comment`
- `get_issue_comments`

### **Pull Request Management (14 tools)**
- `list_pull_requests`
- `get_pull_request`
- `create_pull_request`
- `update_pull_request`
- `merge_pull_request`
- `get_pull_request_comments`
- `get_pull_request_diff`
- `get_pull_request_files`
- `get_pull_request_reviews`
- `get_pull_request_status`
- `update_pull_request_branch`
- `create_pending_pull_request_review`
- `submit_pending_pull_request_review`
- `delete_pending_pull_request_review`

### **Search Operations (3 tools)**
- `search_repositories`
- `search_code`
- `search_issues`

### **Security/Code Analysis (3 tools)**
- `list_code_scanning_alerts`
- `get_code_scanning_alert`
- `list_commits`

### **GitHub Copilot (2 tools)**
- `assign_copilot_to_issue`
- `request_copilot_review`

## 🚀 **How to Test the Fixed Version**

### **1. Test Tool Discovery**
```bash
cd github_integration
python github_client_fixed.py discover
```

### **2. Test Fixed GitHub Client**
```bash
python github_client_fixed.py
```

### **3. Test Fixed Unified Client**
```bash
python unified_client_fixed.py
```

### **4. Interactive Mode**
```bash
python unified_client_fixed.py interactive
```

## 💡 **Key Lessons**

### **1. Always Do Tool Discovery**
```python
# Don't assume tool names - discover them!
tools = await client.get_available_tools()
print(f"Available tools: {tools}")
```

### **2. Check Tool Descriptions**
```python
# Get detailed info about each tool
for tool_name in tools:
    tool_info = await client.get_tool_info(tool_name)
    print(f"{tool_name}: {tool_info.get('description')}")
```

### **3. Handle Missing Tools Gracefully**
```python
# Instead of assuming list_repositories exists:
try:
    repos = await client.call_tool("list_repositories")
except ValueError as e:
    # Fallback to search
    repos = await client.call_tool("search_repositories", {"query": "user:username"})
```

## 🔄 **Migration Guide**

If you're using the original files, update to the fixed versions:

### **Old (Broken)**
```python
from github_client import GitHubMCPClient          # ❌ Has wrong tool names
await client.list_repositories()                   # ❌ Tool doesn't exist
```

### **New (Fixed)**  
```python
from github_client_fixed import FixedGitHubMCPClient  # ✅ Correct tool names
await client.search_repositories("user:username")     # ✅ Uses actual tool
await client.get_my_repositories()                    # ✅ Convenience method
```

## 🎯 **Quick Fix Commands**

```bash
# Use the fixed clients instead:
python github_client_fixed.py              # Instead of github_client.py
python unified_client_fixed.py             # Instead of unified_client.py

# Or discover tools yourself:
python github_client_fixed.py discover     # See all available tools
```

The fixed versions work with the **actual** GitHub MCP server tools, not the assumed ones! 🚀

---

**Bottom Line**: Always check what tools are **actually available** rather than assuming based on documentation or expectations. The GitHub MCP server evolved and has different tool names than initially expected.
