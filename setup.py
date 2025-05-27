from setuptools import setup, find_packages

setup(
    name="simple-file-mcp-server",
    version="1.0.0",
    description="A simple MCP server for file operations - learning example",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "simple-file-mcp-server=server:main",
        ],
    },
)