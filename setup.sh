#!/bin/bash

# MCP Filesystem & GitHub Server Setup Script

echo "🚀 MCP Filesystem & GitHub Server Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
echo "✅ Found: $python_version"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
if [[ $? -ne 0 ]]; then
    echo "❌ Error: Failed to install dependencies"
    echo "Try running: pip3 install -r requirements.txt manually"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check for GitHub token
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "⚠️  Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set"
    echo ""
    echo "To enable GitHub features:"
    echo "1. Get a token from: https://github.com/settings/tokens"
    echo "2. Run: export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here"
    echo ""
    echo "GitHub features will be disabled until token is set."
else
    echo "✅ GitHub token found"
fi
echo ""

# Create test directory
echo "Creating test directory..."
mkdir -p test_workspace
echo "✅ Created test_workspace/"
echo ""

# Test servers
echo "Testing servers..."
echo ""

# Test filesystem server
echo "1. Testing Filesystem Server..."
cd test_workspace
timeout 5 python3 ../filesystem_server.py &
server_pid=$!
sleep 2
if ps -p $server_pid > /dev/null; then
    echo "✅ Filesystem server starts successfully"
    kill $server_pid 2>/dev/null
else
    echo "❌ Filesystem server failed to start"
fi
cd ..

# Test GitHub server (if token is set)
if [ ! -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo ""
    echo "2. Testing GitHub Server..."
    timeout 5 python3 github_server.py &
    server_pid=$!
    sleep 2
    if ps -p $server_pid > /dev/null; then
        echo "✅ GitHub server starts successfully"
        kill $server_pid 2>/dev/null
    else
        echo "❌ GitHub server failed to start"
    fi
fi

# Test unified server
echo ""
echo "3. Testing Unified Server..."
timeout 5 python3 unified_server.py &
server_pid=$!
sleep 2
if ps -p $server_pid > /dev/null; then
    echo "✅ Unified server starts successfully"
    kill $server_pid 2>/dev/null
else
    echo "❌ Unified server failed to start"
fi

echo ""
echo "======================================"
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run a server:"
echo "   python3 filesystem_server.py     # Filesystem only"
echo "   python3 github_server.py         # GitHub only"
echo "   python3 unified_server.py        # Both (recommended)"
echo ""
echo "2. In another terminal, use the client:"
echo "   python3"
echo "   >>> from fastmcp_client import FastMCPClient"
echo "   >>> # See README.md for usage examples"
echo ""
echo "3. Run tests:"
echo "   python3 integration_test.py"
echo "   python3 test_github_integration.py"
echo ""
echo "Happy coding! 🎉"
