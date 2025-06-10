#!/usr/bin/env python3

"""
Quick Start Example - Using LangChain to build a development assistant
This shows how to quickly recreate Claude's capabilities using existing frameworks
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseLanguageModel
import aiofiles
import asyncio
import aiohttp


class QuickDevAssistant:
    """Quick development assistant using LangChain"""
    
    def __init__(self, openai_api_key: str, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=0.1)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Set up tools
        self.tools = self._create_tools()
        
        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=10
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create the tools that the agent can use"""
        
        return [
            Tool(
                name="list_files",
                description="List files and directories in a given path. Input should be a directory path.",
                func=self._list_files
            ),
            Tool(
                name="read_file", 
                description="Read the contents of a file. Input should be a file path.",
                func=self._read_file
            ),
            Tool(
                name="write_file",
                description="Write content to a file. Input should be JSON: {'filepath': 'path', 'content': 'content'}",
                func=self._write_file
            ),
            Tool(
                name="create_directory",
                description="Create a new directory. Input should be a directory path.",
                func=self._create_directory
            ),
            Tool(
                name="web_search",
                description="Search for information on the web. Input should be a search query.",
                func=self._web_search
            ),
            Tool(
                name="analyze_codebase",
                description="Analyze the current codebase structure and patterns. No input needed.",
                func=self._analyze_codebase
            )
        ]
    
    def _list_files(self, directory: str = ".") -> str:
        """List files in directory"""
        try:
            target_dir = self.base_dir / directory
            files = []
            
            for item in target_dir.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return json.dumps(files, indent=2)
        except Exception as e:
            return f"Error listing files: {e}"
    
    def _read_file(self, filepath: str) -> str:
        """Read file contents"""
        try:
            target_file = self.base_dir / filepath
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Truncate very long files
                if len(content) > 5000:
                    return content[:5000] + "\n\n... (file truncated for brevity)"
                return content
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _write_file(self, input_data: str) -> str:
        """Write content to file"""
        try:
            data = json.loads(input_data)
            filepath = data['filepath']
            content = data['content']
            
            target_file = self.base_dir / filepath
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def _create_directory(self, directory: str) -> str:
        """Create directory"""
        try:
            target_dir = self.base_dir / directory
            target_dir.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {directory}"
        except Exception as e:
            return f"Error creating directory: {e}"
    
    def _web_search(self, query: str) -> str:
        """Search the web (simplified version)"""
        # This is a placeholder - integrate with real search API
        return f"Web search results for '{query}': This would contain real search results from Brave Search, Google, etc."
    
    def _analyze_codebase(self, _: str = "") -> str:
        """Analyze the current codebase"""
        try:
            analysis = {
                "project_structure": [],
                "python_files": [],
                "key_patterns": [],
                "technologies": []
            }
            
            # Get project structure
            for item in self.base_dir.rglob("*"):
                if item.is_file() and not any(part.startswith('.') for part in item.parts):
                    rel_path = item.relative_to(self.base_dir)
                    analysis["project_structure"].append(str(rel_path))
                    
                    if item.suffix == '.py':
                        analysis["python_files"].append(str(rel_path))
            
            # Basic pattern detection
            for py_file in analysis["python_files"][:5]:  # Analyze first 5 Python files
                try:
                    content = self._read_file(py_file)
                    if "async def" in content:
                        analysis["key_patterns"].append(f"Async programming in {py_file}")
                    if "class" in content:
                        analysis["key_patterns"].append(f"OOP patterns in {py_file}")
                    if "fastmcp" in content.lower():
                        analysis["technologies"].append("FastMCP")
                    if "asyncio" in content:
                        analysis["technologies"].append("AsyncIO")
                except:
                    continue
            
            return json.dumps(analysis, indent=2)
        except Exception as e:
            return f"Error analyzing codebase: {e}"
    
    def run(self, task: str) -> str:
        """Run a development task"""
        return self.agent.run(task)


def demo_quick_assistant():
    """Demonstrate the quick development assistant"""
    
    # You need OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    assistant = QuickDevAssistant(api_key, "/Users/sathishravichandan/mcp-play/fileSystem")
    
    # Example tasks (similar to what Claude did)
    tasks = [
        "Analyze the current codebase structure and identify the main components",
        
        "Create a new integration directory called 'quick_integration' and write a simple HTTP client that can work with the existing FastMCPClient",
        
        "Write a configuration file for the integration with example settings",
        
        "Create documentation explaining how to use the new integration"
    ]
    
    print("🚀 Quick Development Assistant Demo")
    print("=" * 50)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n📋 Task {i}: {task}")
        print("-" * 30)
        
        try:
            result = assistant.run(task)
            print(f"✅ Result:\n{result}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue to next task...")
    
    print("\n🎉 Demo complete! Check the generated files.")


def interactive_mode():
    """Interactive mode for the assistant"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    assistant = QuickDevAssistant(api_key, "/Users/sathishravichandan/mcp-play/fileSystem")
    
    print("🎉 Quick Development Assistant - Interactive Mode")
    print("Type your development tasks in natural language!")
    print("Examples:")
    print("  - 'Create a REST API client for my project'")
    print("  - 'Add error handling to the filesystem server'") 
    print("  - 'Write tests for the FastMCP client'")
    print("  - 'Generate documentation for the project'")
    print("\nType 'quit' to exit")
    
    while True:
        try:
            task = input("\n🤖 What would you like me to do? ")
            
            if task.lower() in ['quit', 'exit', 'q']:
                break
            
            if not task.strip():
                continue
            
            print(f"\n⚙️ Working on: {task}")
            print("-" * 50)
            
            result = assistant.run(task)
            print(f"\n✅ Completed!\n{result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n👋 Thanks for using the Quick Development Assistant!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        demo_quick_assistant()
