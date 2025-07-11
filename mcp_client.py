#!/usr/bin/env python3
"""
MCP Client for AWS Diagram MCP Server

This client connects to the scp-diagram-mcp-server and provides a simple interface
to interact with all available tools: generate_diagram, get_diagram_examples, and list_icons.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, Any, Optional, List


class MCPResponse:
    """Response from MCP server"""
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error


class MCPClient:
    """Client for communicating with MCP servers via subprocess"""
    
    def __init__(self, server_command: List[str]):
        """
        Initialize MCP client
        
        Args:
            server_command: Command and arguments to start the MCP server
        """
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def connect(self):
        """Connect to the MCP server"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize the connection
            await self._send_initialize()
            
        except Exception as e:
            raise ConnectionError(f"Failed to start MCP server: {e}")
    
    async def close(self):
        """Close connection to MCP server"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except:
                pass
            self.process = None
    
    async def _send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response"""
        if not self.process:
            raise ConnectionError("Not connected to MCP server")
        
        # Send message
        message_str = json.dumps(message) + '\n'
        self.process.stdin.write(message_str.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise ConnectionError("No response from MCP server")
        
        try:
            response = json.loads(response_line.decode().strip())
            return response
        except json.JSONDecodeError as e:
            raise ConnectionError(f"Invalid JSON response: {e}")
    
    async def _send_initialize(self):
        """Send initialize message to MCP server"""
        self.request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_message(message)
        if "error" in response:
            raise ConnectionError(f"Initialize failed: {response['error']}")
        
        # Send initialized notification
        self.request_id += 1
        initialized_message = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }
        
        # Send without expecting response (notification)
        message_str = json.dumps(initialized_message) + '\n'
        self.process.stdin.write(message_str.encode())
        await self.process.stdin.drain()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> MCPResponse:
        """
        Call a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            MCPResponse with success status and data/error
        """
        if arguments is None:
            arguments = {}
        
        self.request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self._send_message(message)
            
            if "error" in response:
                return MCPResponse(success=False, error=str(response["error"]))
            
            if "result" in response:
                return MCPResponse(success=True, data=response["result"])
            
            return MCPResponse(success=False, error="No result in response")
            
        except Exception as e:
            return MCPResponse(success=False, error=str(e))


class DiagramMCPClient:
    """High-level client for AWS Diagram MCP Server"""
    
    def __init__(self, server_command: Optional[List[str]] = None):
        """
        Initialize the diagram MCP client
        
        Args:
            server_command: Command to start the server. Defaults to uvx command.
        """
        if server_command is None:
            server_command = ["uv", "run", "python", "-m", "server"]
        
        # Set working directory for server execution
        self.server_cwd = "/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server"
        
        self.mcp_client = MCPClient(server_command)
        self.workspace_dir = os.getcwd()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.mcp_client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.mcp_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def list_icons(self, provider_filter: str = None, service_filter: str = None) -> MCPResponse:
        """
        List available icons from the diagrams package
        
        Args:
            provider_filter: Filter by provider (e.g., "aws", "gcp", "k8s")
            service_filter: Filter by service (e.g., "compute", "database")
            
        Returns:
            MCPResponse with icon data
        """
        args = {}
        if provider_filter:
            args["provider_filter"] = provider_filter
        if service_filter:
            args["service_filter"] = service_filter
            
        return await self.mcp_client.call_tool("list_icons", args)
    
    async def get_diagram_examples(self, diagram_type: str = "all") -> MCPResponse:
        """
        Get example code for different types of diagrams
        
        Args:
            diagram_type: Type of examples to get (aws, sequence, flow, class, k8s, onprem, custom, all)
            
        Returns:
            MCPResponse with example code
        """
        args = {"diagram_type": diagram_type}
        return await self.mcp_client.call_tool("get_diagram_examples", args)
    
    async def generate_diagram(self, code: str, filename: str = None, timeout: int = 90) -> MCPResponse:
        """
        Generate a diagram from Python code
        
        Args:
            code: Python code using diagrams package
            filename: Optional filename for the diagram
            timeout: Timeout in seconds (default 90)
            
        Returns:
            MCPResponse with generated diagram path
        """
        args = {
            "code": code,
            "timeout": timeout,
            "workspace_dir": self.workspace_dir
        }
        
        if filename:
            args["filename"] = filename
            
        return await self.mcp_client.call_tool("generate_diagram", args)


# Test functions
async def test_list_icons():
    """Test the list_icons functionality"""
    print("=== Testing list_icons ===")
    
    async with DiagramMCPClient() as client:
        # Test 1: List all providers
        print("1. Listing all providers...")
        response = await client.list_icons()
        if response.success:
            providers = response.data.get("content", [])
            print(f"Found {len(providers)} providers: {[p.get('name') for p in providers[:5]]}")
        else:
            print(f"Error: {response.error}")
        
        # Test 2: List AWS services
        print("\n2. Listing AWS services...")
        response = await client.list_icons(provider_filter="aws")
        if response.success:
            services = response.data.get("content", [])
            print(f"Found {len(services)} AWS services: {[s.get('name') for s in services[:5]]}")
        else:
            print(f"Error: {response.error}")
        
        # Test 3: List AWS compute icons
        print("\n3. Listing AWS compute icons...")
        response = await client.list_icons(provider_filter="aws", service_filter="compute")
        if response.success:
            icons = response.data.get("content", [])
            print(f"Found {len(icons)} AWS compute icons: {[i.get('name') for i in icons[:5]]}")
        else:
            print(f"Error: {response.error}")


async def test_get_examples():
    """Test the get_diagram_examples functionality"""
    print("\n=== Testing get_diagram_examples ===")
    
    async with DiagramMCPClient() as client:
        # Test different diagram types
        for diagram_type in ["aws", "sequence", "flow"]:
            print(f"\n{diagram_type.upper()} Examples:")
            response = await client.get_diagram_examples(diagram_type)
            if response.success:
                examples = response.data.get("content", {})
                example_names = list(examples.keys())
                print(f"Found {len(example_names)} examples: {example_names}")
                
                # Show first example code
                if example_names:
                    first_example = examples[example_names[0]]
                    code_lines = first_example.get("code", "").split('\n')
                    print(f"First example ({example_names[0]}):")
                    for line in code_lines[:3]:  # Show first 3 lines
                        print(f"  {line}")
                    if len(code_lines) > 3:
                        print(f"  ... ({len(code_lines) - 3} more lines)")
            else:
                print(f"Error: {response.error}")


async def test_generate_diagram():
    """Test the generate_diagram functionality"""
    print("\n=== Testing generate_diagram ===")
    
    async with DiagramMCPClient() as client:
        # Simple AWS diagram
        code = '''
with Diagram("Simple Web Service", show=False):
    ELB("load balancer") >> EC2("web server") >> RDS("database")
'''
        
        print("Generating simple AWS diagram...")
        response = await client.generate_diagram(code, filename="test_simple_aws")
        
        if response.success:
            result = response.data.get("content", {})
            if result.get("success"):
                print(f"✅ Diagram generated successfully!")
                print(f"📁 File path: {result.get('file_path')}")
                print(f"📊 Details: {result.get('message', 'No details')}")
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.error}")


async def run_all_tests():
    """Run all test functions"""
    print("🚀 Starting MCP Client Tests for AWS Diagram Server\n")
    
    try:
        await test_list_icons()
        await test_get_examples()
        await test_generate_diagram()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests (compatible with older Python versions)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_all_tests())
    finally:
        loop.close()