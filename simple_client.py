#!/usr/bin/env python3
"""
Simple MCP Client for AWS Diagram MCP Server

This client uses the mcp library to connect directly to the server
"""

import asyncio
import os
import sys
import json
import tempfile
from pathlib import Path

# Try to import mcp - if not available, provide instructions
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ MCP library not found. Install it with:")
    print("pip install mcp")
    sys.exit(1)


class DiagramClient:
    """Simple client for AWS Diagram MCP Server"""
    
    def __init__(self):
        self.workspace_dir = os.getcwd()
    
    async def test_server(self):
        """Test all server capabilities"""
        # Server parameters
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "server"],
            env={"FASTMCP_LOG_LEVEL": "ERROR"},
            cwd="/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server"
        )
        
        print("🚀 Testing AWS Diagram MCP Server\n")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                
                # Test 1: List available tools
                print("=== Available Tools ===")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"• {tool.name}: {tool.description[:100]}...")
                
                print(f"\nFound {len(tools.tools)} tools\n")
                
                # Test 2: List icons (without filters first)
                print("=== Testing list_icons ===")
                try:
                    result = await session.call_tool("list_icons", {})
                    if result.content:
                        data = result.content[0].text if result.content else "{}"
                        parsed = json.loads(data)
                        providers = parsed.get("content", [])
                        print(f"✅ Found {len(providers)} providers")
                        if providers:
                            print(f"First few providers: {[p.get('name') for p in providers[:5]]}")
                    else:
                        print("❌ No content in response")
                except Exception as e:
                    print(f"❌ Error calling list_icons: {e}")
                
                # Test 3: Get AWS icons
                print("\n--- AWS Icons ---")
                try:
                    result = await session.call_tool("list_icons", {
                        "provider_filter": "aws"
                    })
                    if result.content:
                        data = result.content[0].text if result.content else "{}"
                        parsed = json.loads(data)
                        services = parsed.get("content", [])
                        print(f"✅ Found {len(services)} AWS services")
                        if services:
                            print(f"AWS services: {[s.get('name') for s in services[:10]]}")
                except Exception as e:
                    print(f"❌ Error getting AWS icons: {e}")
                
                # Test 4: Get diagram examples
                print("\n=== Testing get_diagram_examples ===")
                try:
                    result = await session.call_tool("get_diagram_examples", {
                        "diagram_type": "aws"
                    })
                    if result.content:
                        data = result.content[0].text if result.content else "{}"
                        parsed = json.loads(data)
                        examples = parsed.get("content", {})
                        print(f"✅ Found {len(examples)} AWS examples")
                        example_names = list(examples.keys())[:3]
                        print(f"Example names: {example_names}")
                except Exception as e:
                    print(f"❌ Error getting examples: {e}")
                
                # Test 5: Generate a simple diagram
                print("\n=== Testing generate_diagram ===")
                
                # Simple diagram code
                diagram_code = '''
with Diagram("Simple Web Service", show=False, direction="LR"):
    user = Generic("User")
    lb = ELB("Load Balancer")
    web = EC2("Web Server")
    db = RDS("Database")
    
    user >> lb >> web >> db
'''
                
                try:
                    result = await session.call_tool("generate_diagram", {
                        "code": diagram_code,
                        "filename": "test_simple_web_service",
                        "workspace_dir": self.workspace_dir
                    })
                    
                    if result.content:
                        data = result.content[0].text if result.content else "{}"
                        parsed = json.loads(data)
                        content = parsed.get("content", {})
                        
                        if content.get("success"):
                            print("✅ Diagram generated successfully!")
                            print(f"📁 File: {content.get('file_path')}")
                            print(f"💬 Message: {content.get('message')}")
                            
                            # Check if file exists
                            file_path = content.get('file_path')
                            if file_path and os.path.exists(file_path):
                                print(f"✅ File confirmed to exist: {file_path}")
                                print(f"📏 File size: {os.path.getsize(file_path)} bytes")
                        else:
                            print(f"❌ Diagram generation failed: {content.get('error')}")
                    else:
                        print("❌ No content in response")
                        
                except Exception as e:
                    print(f"❌ Error generating diagram: {e}")
                
                print("\n🎉 All tests completed!")


async def main():
    """Main function"""
    client = DiagramClient()
    await client.test_server()


if __name__ == "__main__":
    # Check if uvx is available
    import subprocess
    try:
        subprocess.run(["uvx", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uvx not found. Install with:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("export PATH=\"$HOME/.local/bin:$PATH\"")
        sys.exit(1)
    
    # Run the client
    asyncio.run(main())