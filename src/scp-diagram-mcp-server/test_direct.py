#!/usr/bin/env python3
"""
Direct test of scp-diagram-mcp-server functionality
This bypasses MCP protocol and tests the server tools directly
"""

import asyncio
import sys
import os
import json

# Add the server module to path
sys.path.insert(0, '/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server')

from awslabs.aws_diagram_mcp_server.diagrams_tools import (
    generate_diagram,
    get_diagram_examples,
    list_diagram_icons,
)
from awslabs.aws_diagram_mcp_server.models import DiagramType


async def test_direct_functions():
    """Test server functions directly"""
    print("🔧 Testing AWS Diagram Server Functions Directly\n")
    
    # Test 1: List icons
    print("=== Testing list_diagram_icons ===")
    try:
        # List all providers
        result = list_diagram_icons(None, None)
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Result attributes: {dir(result)}")
        
        # Check providers
        if hasattr(result, 'providers'):
            providers = result.providers
            print(f"✅ Providers found: {len(providers)} total")
            provider_names = list(providers.keys())[:5]
            print(f"Provider names: {provider_names}")
        
        # List AWS services
        result_aws = list_diagram_icons("aws", None)
        if hasattr(result_aws, 'providers') and 'aws' in result_aws.providers:
            aws_services = result_aws.providers['aws']
            print(f"✅ AWS services found: {len(aws_services)}")
            service_names = list(aws_services.keys())[:10]
            print(f"AWS services: {service_names}")
            
    except Exception as e:
        print(f"❌ Error in list_diagram_icons: {e}")
    
    # Test 2: Get examples
    print("\n=== Testing get_diagram_examples ===")
    try:
        result = get_diagram_examples(DiagramType.AWS)
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Result attributes: {dir(result)}")
        
        if hasattr(result, 'examples'):
            examples = result.examples
            print(f"✅ AWS examples found: {len(examples)}")
            example_names = list(examples.keys())
            print(f"Example names: {example_names}")
            
            if example_names:
                first_example_code = examples[example_names[0]]
                print(f"\nFirst example ({example_names[0]}):")
                code_lines = first_example_code.split('\n')[:5]
                for line in code_lines:
                    print(f"  {line}")
            
    except Exception as e:
        print(f"❌ Error in get_diagram_examples: {e}")
    
    # Test 3: Generate diagram
    print("\n=== Testing generate_diagram ===")
    try:
        workspace_dir = "/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server"
        
        # Simple diagram code
        code = '''
with Diagram("Simple Web Service", show=False, direction="LR"):
    user = Generic("User")
    lb = ELB("Load Balancer") 
    web = EC2("Web Server")
    db = RDS("Database")
    
    user >> lb >> web >> db
'''
        
        result = await generate_diagram(
            code=code,
            filename="direct_test_diagram",
            timeout=90,
            workspace_dir=workspace_dir
        )
        
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Result attributes: {dir(result)}")
        
        if hasattr(result, 'status'):
            if result.status == 'success':
                print("✅ Diagram generated successfully!")
                print(f"📁 File path: {result.path}")
                print(f"💬 Message: {result.message}")
                
                # Check if file exists
                if result.path and os.path.exists(result.path):
                    print(f"✅ File confirmed: {os.path.basename(result.path)}")
                    print(f"📏 Size: {os.path.getsize(result.path)} bytes")
                else:
                    print(f"❌ File not found: {result.path}")
            else:
                print(f"❌ Generation failed: {result.message}")
            
    except Exception as e:
        print(f"❌ Error in generate_diagram: {e}")
    
    print("\n🎉 Direct testing completed!")


if __name__ == "__main__":
    asyncio.run(test_direct_functions())