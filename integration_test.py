#!/usr/bin/env python3
"""
Integration test script for MCP filesystem client
Suitable for running in GitHub Actions
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path so we can import our client
sys.path.append('.')
from fastmcp_client import FastMCPClient


async def run_integration_tests():
    """Run comprehensive integration tests"""

    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="mcp_test_")
    original_cwd = os.getcwd()

    try:
        # Change to test directory
        os.chdir(test_dir)
        print(f"🧪 Running tests in: {test_dir}")

        # Copy our server to the test directory
        server_path = Path(original_cwd) / "filesystem_server.py"
        shutil.copy2(server_path, "filesystem_server.py")

        # Start the client
        client = FastMCPClient(["python3", "filesystem_server.py"])

        print("🚀 Starting MCP server...")
        await client.start()
        await client.initialize()

        # Test 1: Get working directory
        print("\n📁 Test 1: Get working directory")
        result = await client.call_tool("get_working_directory")
        print(f"✅ Working directory: {result}")

        # Test 2: List empty directory
        print("\n📋 Test 2: List files in empty directory")
        result = await client.call_tool("list_files", {"directory": "."})
        print(f"✅ Listed files: {result}")

        # Test 3: Create a test file
        print("\n📝 Test 3: Write a test file")
        test_content = "Hello from GitHub Actions!\nThis is a test file."
        result = await client.call_tool("write_file", {
            "filepath": "test.txt",
            "content": test_content
        })
        print(f"✅ File written: {result}")

        # Test 4: Read the test file
        print("\n📖 Test 4: Read the test file")
        result = await client.call_tool("read_file", {"filepath": "test.txt"})
        print(f"✅ File read: {result}")

        # Verify content - extract text from FastMCP response format
        content_found = False
        if isinstance(result, dict) and 'content' in result:
            for content_item in result['content']:
                if content_item.get('type') == 'text':
                    file_text = content_item.get('text', '')
                    if test_content in file_text:
                        content_found = True
                        break

        # Also check if content is directly in the result string
        if not content_found and test_content in str(result):
            content_found = True

        if content_found:
            print("✅ File content matches expected")
        else:
            print("❌ File content mismatch!")
            print(f"Expected to find: '{test_content}'")
            print(f"Got result: {result}")
            return False

        # Test 5: Create a directory
        print("\n📂 Test 5: Create directory")
        result = await client.call_tool("create_directory", {"directory": "subdir"})
        print(f"✅ Directory created: {result}")

        # Test 6: Write file in subdirectory
        print("\n📄 Test 6: Write file in subdirectory")
        result = await client.call_tool("write_file", {
            "filepath": "subdir/nested.txt",
            "content": "Nested file content"
        })
        print(f"✅ Nested file written: {result}")

        # Test 7: List directory with files
        print("\n📋 Test 7: List directory with files")
        result = await client.call_tool("list_files", {"directory": "."})
        print(f"✅ Directory listing: {result}")

        # Test 8: List subdirectory
        print("\n📋 Test 8: List subdirectory")
        result = await client.call_tool("list_files", {"directory": "subdir"})
        print(f"✅ Subdirectory listing: {result}")

        # Test 9: Error handling - try to read non-existent file
        print("\n🚫 Test 9: Error handling - read non-existent file")
        try:
            result = await client.call_tool("read_file", {"filepath": "nonexistent.txt"})

            # Check if error is properly handled
            error_found = False
            result_str = str(result)

            if "Error" in result_str or "does not exist" in result_str:
                error_found = True
            elif isinstance(result, dict) and 'content' in result:
                for content_item in result['content']:
                    if content_item.get('type') == 'text':
                        text_content = content_item.get('text', '')
                        if "Error" in text_content or "does not exist" in text_content:
                            error_found = True
                            break

            if error_found:
                print("✅ Error handling works correctly")
            else:
                print(f"❌ Unexpected result for non-existent file: {result}")
                return False

        except Exception as e:
            print(f"✅ Exception caught as expected: {e}")

        # Test 10: Security test - try to access outside directory
        print("\n🔒 Test 10: Security test - access outside directory")
        try:
            result = await client.call_tool("read_file", {"filepath": "../../../etc/passwd"})

            # Check if security is properly enforced
            security_ok = False
            result_str = str(result)

            if "Error" in result_str and "Access denied" in result_str:
                security_ok = True
            elif isinstance(result, dict) and 'content' in result:
                for content_item in result['content']:
                    if content_item.get('type') == 'text':
                        text_content = content_item.get('text', '')
                        if "Error" in text_content and "Access denied" in text_content:
                            security_ok = True
                            break

            if security_ok:
                print("✅ Security check works correctly")
            else:
                print(f"❌ Security vulnerability detected: {result}")
                return False

        except Exception as e:
            print(f"✅ Security exception caught: {e}")

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        try:
            await client.close()
        except:
            pass

        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)


async def performance_test():
    """Run performance tests"""
    print("\n⚡ Running performance tests...")

    client = FastMCPClient(["python3", "filesystem_server.py"])

    try:
        await client.start()
        await client.initialize()

        # Test multiple rapid calls
        import time
        start_time = time.time()

        for i in range(10):
            await client.call_tool("get_working_directory")

        end_time = time.time()
        avg_time = (end_time - start_time) / 10

        print(f"✅ Average response time: {avg_time:.3f}s")

        if avg_time < 1.0:  # Should be fast
            print("✅ Performance test passed")
            return True
        else:
            print("❌ Performance test failed - too slow")
            return False

    finally:
        await client.close()


async def main():
    """Main test runner"""
    print("🧪 MCP Client Integration Tests")
    print("=" * 50)

    # Run integration tests
    integration_success = await run_integration_tests()

    # Run performance tests
    performance_success = await performance_test()

    # Final result
    if integration_success and performance_success:
        print("\n🎉 All tests passed! ✅")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())