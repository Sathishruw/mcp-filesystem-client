#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FastMCPClient:
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        self.pending_requests = {}
        self.tools = {}
        self.capabilities = {}

    async def start(self):
        """Start the MCP server process"""
        logger.info(f"Starting server: {' '.join(self.server_command)}")

        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        logger.info(f"Server started with PID: {self.process.pid}")

        # Start background tasks
        asyncio.create_task(self._read_stdout())
        asyncio.create_task(self._read_stderr())

        # Wait a moment for server to initialize
        await asyncio.sleep(0.5)

    async def _read_stdout(self):
        """Read responses from server stdout"""
        buffer = ""
        while True:
            try:
                data = await self.process.stdout.read(1024)
                if not data:
                    break

                buffer += data.decode('utf-8')

                # Process complete JSON messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        try:
                            message = json.loads(line)
                            await self._handle_message(message)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON: {line} - {e}")

            except Exception as e:
                logger.error(f"Error reading stdout: {e}")
                break

    async def _read_stderr(self):
        """Read error messages from server stderr"""
        while True:
            try:
                line = await self.process.stderr.readline()
                if not line:
                    break
                error_msg = line.decode('utf-8').strip()
                if error_msg:
                    logger.info(f"Server: {error_msg}")
            except Exception as e:
                logger.error(f"Error reading stderr: {e}")
                break

    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming message from server"""
        logger.debug(f"Received: {message}")

        if 'id' in message and message['id'] in self.pending_requests:
            # Response to our request
            future = self.pending_requests.pop(message['id'])
            if not future.done():
                future.set_result(message)
        else:
            # Notification or other message
            logger.info(f"Notification: {message}")

    async def _send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to server and optionally wait for response"""
        message_json = json.dumps(message) + '\n'
        logger.debug(f"Sending: {message}")

        self.process.stdin.write(message_json.encode('utf-8'))
        await self.process.stdin.drain()

        # If this message has an ID, wait for response
        if 'id' in message:
            future = asyncio.Future()
            self.pending_requests[message['id']] = future

            try:
                response = await asyncio.wait_for(future, timeout=10.0)
                return response
            except asyncio.TimeoutError:
                self.pending_requests.pop(message['id'], None)
                raise TimeoutError(f"Request {message['id']} timed out")

    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    async def initialize(self):
        """Initialize MCP connection"""
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "fastmcp-client",
                    "version": "1.0.0"
                }
            }
        }

        response = await self._send_message(init_request)

        if 'result' in response:
            self.capabilities = response['result'].get('capabilities', {})
            logger.info(f"Server capabilities: {self.capabilities}")
        elif 'error' in response:
            raise Exception(f"Initialization failed: {response['error']}")

        # Send initialized notification
        await self._send_message({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })

        # Get available tools
        await self._list_tools()

    async def _list_tools(self):
        """List available tools"""
        tools_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }

        response = await self._send_message(tools_request)

        if 'result' in response and 'tools' in response['result']:
            self.tools = {tool['name']: tool for tool in response['result']['tools']}
            logger.info(f"Available tools: {list(self.tools.keys())}")
        elif 'error' in response:
            logger.error(f"Failed to list tools: {response['error']}")

    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not available. Available: {list(self.tools.keys())}")

        call_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }

        response = await self._send_message(call_request)

        if 'result' in response:
            return response['result']
        elif 'error' in response:
            raise Exception(f"Tool call failed: {response['error']}")
        else:
            raise Exception(f"Unexpected response: {response}")

    async def close(self):
        """Close connection"""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()


async def test_filesystem_server():
    """Test the filesystem server"""
    client = FastMCPClient([
        "python3",
        "/Users/sathishravichandan/mcp-play/fileSystem/filesystem_server.py"
    ])

    try:
        # Start and initialize
        await client.start()
        await client.initialize()

        print(f"\n✅ Connected successfully!")
        print(f"Available tools: {list(client.tools.keys())}")

        # Test get_working_directory
        print(f"\n📁 Getting working directory...")
        result = await client.call_tool("get_working_directory")
        print(f"Result: {result}")

        # Test list_files
        print(f"\n📋 Listing files in current directory...")
        result = await client.call_tool("list_files", {"directory": "."})
        print(f"Result: {result}")

        # Test read_file (if there's a file to read)
        print(f"\n📄 Trying to read filesystem_server.py...")
        try:
            result = await client.call_tool("read_file", {"filepath": "filesystem_server.py"})
            # Just show first 200 chars
            if isinstance(result.get('content'), list) and result['content']:
                content = result['content'][0].get('text', '')[:200]
                print(f"File content preview: {content}...")
            else:
                print(f"Result: {str(result)[:200]}...")
        except Exception as e:
            print(f"Could not read file: {e}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def interactive_mode():
    """Interactive mode for testing"""
    client = FastMCPClient([
        "python3",
        "/Users/sathishravichandan/mcp-play/fileSystem/filesystem_server.py"
    ])

    try:
        await client.start()
        await client.initialize()

        print(f"\n🎉 Connected to filesystem server!")
        print(f"Available tools: {', '.join(client.tools.keys())}")
        print(f"\nType 'help' for commands, 'quit' to exit")

        while True:
            try:
                command = input("\n> ").strip()

                if command == 'quit':
                    break
                elif command == 'help':
                    print("Available commands:")
                    print("  list [directory]     - List files in directory (default: current)")
                    print("  read <filepath>      - Read a file")
                    print("  write <filepath>     - Write to a file (will prompt for content)")
                    print("  mkdir <directory>    - Create directory")
                    print("  pwd                  - Show working directory")
                    print("  tools                - Show available tools")
                    print("  quit                 - Exit")

                elif command == 'tools':
                    for name, tool in client.tools.items():
                        print(f"  {name}: {tool.get('description', 'No description')}")

                elif command == 'pwd':
                    result = await client.call_tool("get_working_directory")
                    print(result)

                elif command.startswith('list'):
                    parts = command.split()
                    directory = parts[1] if len(parts) > 1 else "."
                    result = await client.call_tool("list_files", {"directory": directory})
                    print(result)

                elif command.startswith('read'):
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: read <filepath>")
                        continue
                    filepath = parts[1]
                    result = await client.call_tool("read_file", {"filepath": filepath})
                    print(result)

                elif command.startswith('write'):
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: write <filepath>")
                        continue
                    filepath = parts[1]
                    print("Enter content (Ctrl+D to finish):")
                    content = sys.stdin.read()
                    result = await client.call_tool("write_file", {"filepath": filepath, "content": content})
                    print(result)

                elif command.startswith('mkdir'):
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: mkdir <directory>")
                        continue
                    directory = parts[1]
                    result = await client.call_tool("create_directory", {"directory": directory})
                    print(result)

                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    except Exception as e:
        logger.error(f"Failed to connect: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(test_filesystem_server())