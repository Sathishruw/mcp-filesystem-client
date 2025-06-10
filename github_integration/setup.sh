#!/bin/bash

# Setup script for GitHub MCP Integration
# This script helps you set up the GitHub MCP integration with your existing filesystem client

echo "🚀 Setting up GitHub MCP Integration..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is available"

# Pull the official GitHub MCP server image
echo "📦 Pulling GitHub MCP server image..."
docker pull ghcr.io/github/github-mcp-server

if [ $? -eq 0 ]; then
    echo "✅ GitHub MCP server image downloaded successfully"
else
    echo "❌ Failed to download GitHub MCP server image"
    exit 1
fi

# Check for GitHub token
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo ""
    echo "⚠️  GitHub Personal Access Token not found in environment variables"
    echo "To use GitHub MCP, you need to:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Create a new personal access token with appropriate permissions"
    echo "3. Export it as an environment variable:"
    echo "   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here"
    echo ""
    echo "Add this to your ~/.zshrc or ~/.bash_profile to make it permanent:"
    echo "   echo 'export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here' >> ~/.zshrc"
else
    echo "✅ GitHub token found in environment"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd "$(dirname "$0")/.."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Installing fastmcp..."
    pip install mcp
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Set your GitHub token (if not already done):"
echo "   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here"
echo ""
echo "2. Test the GitHub client:"
echo "   cd github_integration"
echo "   python github_client.py"
echo ""
echo "3. Try the interactive unified client:"
echo "   python unified_client.py interactive"
echo ""
echo "4. Read the documentation:"
echo "   cat GITHUB_INTEGRATION.md"
