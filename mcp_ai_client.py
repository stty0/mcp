#!/usr/bin/env python3
"""
AI-Powered AWS Diagram Generator using MCP Protocol

Uses AWS Bedrock Claude Sonnet 4 to generate AWS diagrams from natural language prompts
Communicates with AWS Diagram MCP Server via MCP protocol
"""

import asyncio
import os
import sys
import json
import re
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("❌ Boto3 library not found. Install it with:")
    print("pip install boto3")
    sys.exit(1)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ MCP library not found. Install it with:")
    print("uv pip install mcp")
    sys.exit(1)


class MCPAIDiagramGenerator:
    """AI-powered AWS diagram generator using MCP protocol and Bedrock Claude Sonnet 4"""
    
    def __init__(self, region: Optional[str] = None, workspace_dir: Optional[str] = None):
        """
        Initialize the AI diagram generator
        
        Args:
            region: AWS region (if not provided, will use AWS_REGION env var or us-west-2)
            workspace_dir: Directory to save diagrams (defaults to current directory)
        """
        self.region = region or os.getenv('AWS_REGION', 'us-west-2')
        self.model_id = os.getenv('ANTHROPIC_MODEL', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
        self.workspace_dir = workspace_dir or os.getcwd()
        
        # Initialize Bedrock client
        self._init_bedrock_client()
        
        # MCP Server configuration
        self.server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "server"],
            env={
                "FASTMCP_LOG_LEVEL": "CRITICAL",  # Hide non-critical errors like sarif_om
                "PYTHONPATH": "/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server"
            },
            cwd="/home/jrpark/workspace/mcp/src/scp-diagram-mcp-server"
        )
        
        # Cache for MCP server data
        self._providers_cache = None
        self._aws_services_cache = None
        self._examples_cache = None
    
    def _init_bedrock_client(self):
        """Initialize Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
            
            # Test connection
            self._test_bedrock_connection()
            
        except NoCredentialsError:
            raise ValueError(
                "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def _test_bedrock_connection(self):
        """Test Bedrock connection and model access"""
        try:
            test_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            }
            
            self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(test_body)
            )
            
            print(f"✅ Connected to Bedrock with model: {self.model_id}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                raise ValueError(f"Access denied to model {self.model_id}. Check your permissions and model availability in {self.region}")
            elif error_code == 'ValidationException':
                raise ValueError(f"Invalid model ID: {self.model_id}")
            else:
                raise ValueError(f"Bedrock error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to test Bedrock connection: {str(e)}")
    
    async def _call_mcp_server(self, tool_name: str, arguments: dict = None) -> dict:
        """Call MCP server tool"""
        if arguments is None:
            arguments = {}
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(tool_name, arguments)
                
                if result.content:
                    data = result.content[0].text if result.content else "{}"
                    return json.loads(data)
                else:
                    return {}
    
    async def _get_available_icons(self, provider="aws", service=None):
        """Get available icons via MCP"""
        args = {}
        if provider:
            args["provider_filter"] = provider
        if service:
            args["service_filter"] = service
        
        result = await self._call_mcp_server("list_icons", args)
        return result.get("content", {})
    
    async def _get_examples(self, diagram_type="aws"):
        """Get diagram examples via MCP"""
        result = await self._call_mcp_server("get_diagram_examples", {
            "diagram_type": diagram_type
        })
        return result.get("content", {})
    
    def _build_context_prompt(self, aws_services, examples):
        """Build context prompt with available icons and examples"""
        
        # Extract service names and icons
        service_names = []
        compute_icons = []
        database_icons = []
        network_icons = []
        
        if isinstance(aws_services, list):
            # Handle list of services
            for service in aws_services[:15]:
                if isinstance(service, dict) and 'name' in service:
                    service_names.append(service['name'])
        elif isinstance(aws_services, dict):
            # Handle dict of services
            service_names = list(aws_services.keys())[:15]
            compute_icons = aws_services.get('compute', [])[:10]
            database_icons = aws_services.get('database', [])[:8]
            network_icons = aws_services.get('network', [])[:8]
        
        # Extract example code
        example_code = []
        if isinstance(examples, dict):
            example_names = list(examples.keys())[:3]
            for name in example_names:
                code = examples[name]
                if isinstance(code, dict) and 'code' in code:
                    example_code.append(f"# {name}\n{code['code']}")
                elif isinstance(code, str):
                    example_code.append(f"# {name}\n{code}")
        
        context = f"""
You are an AWS diagram code generator. Generate Python code using the diagrams package to create AWS architecture diagrams.

AVAILABLE AWS SERVICES AND ICONS:
- Compute: EC2, ECS, Lambda, EKS, Fargate
- Database: RDS, DynamoDB, DocumentDB, Redshift
- Storage: S3, EBS, EFS
- Network: VPC, ELB, ALB, NLB, CloudFront
- Security: IAM, KMS, WAF
- Analytics: Athena, EMR, Kinesis
- AI/ML: SageMaker, Rekognition, Comprehend
- Application: APIGateway, SQS, SNS

AVAILABLE SERVICES FROM MCP SERVER:
{', '.join(service_names[:20]) if service_names else 'Loading...'}

COMMON PATTERNS:
{chr(10).join(example_code[:2])}

CRITICAL RULES:
1. MUST start with: with Diagram("Architecture Name", show=False):
2. Use standard AWS icon names: EC2, RDS, S3, Lambda, etc.
3. Use >> for connections: service1 >> service2
4. Use Cluster for grouping: with Cluster("name"):
5. NO IMPORTS needed - all icons are pre-imported
6. Keep it simple and functional

CORRECT EXAMPLES:
with Diagram("Web Service with RDS", show=False):
    ELB("lb") >> EC2("web") >> RDS("database")

with Diagram("Serverless API", show=False):
    APIGateway("api") >> Lambda("function") >> DynamoDB("db")

RESPONSE FORMAT:
Return ONLY working Python code with standard AWS service names.
"""
        return context
    
    async def generate_diagram_from_prompt(self, user_prompt: str, filename: Optional[str] = None) -> dict:
        """
        Generate AWS diagram from natural language prompt using MCP server
        
        Args:
            user_prompt: Natural language description of the architecture
            filename: Optional filename for the diagram
            
        Returns:
            Dictionary with generation result
        """
        try:
            print(f"🤖 Processing prompt: {user_prompt}")
            
            # Get context via MCP server
            print("📡 Fetching AWS services and examples from MCP server...")
            aws_services = await self._get_available_icons("aws")
            examples = await self._get_examples("aws")
            
            # Build context prompt
            context = self._build_context_prompt(aws_services, examples)
            
            # Generate code using Bedrock Claude
            print(f"🧠 Generating diagram code with Bedrock Claude Sonnet 4...")
            
            bedrock_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,
                "system": context,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Generate AWS diagram code for: {user_prompt}"
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(bedrock_body)
            )
            
            response_body = json.loads(response['body'].read())
            generated_code = response_body['content'][0]['text'].strip()
            
            # Clean up code (remove markdown formatting if present)
            if "```python" in generated_code:
                match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
                if match:
                    generated_code = match.group(1)
            elif "```" in generated_code:
                match = re.search(r'```\n(.*?)\n```', generated_code, re.DOTALL)
                if match:
                    generated_code = match.group(1)
            
            print("📝 Generated code:")
            print("=" * 50)
            print(generated_code)
            print("=" * 50)
            
            # Generate diagram via MCP server
            print("📡 Sending to MCP server for diagram generation...")
            mcp_result = await self._call_mcp_server("generate_diagram", {
                "code": generated_code,
                "filename": filename,
                "workspace_dir": self.workspace_dir,
                "timeout": 90
            })
            
            # Parse MCP result based on server response format
            if mcp_result.get("status") == "success":
                success = True
                file_path = mcp_result.get("path")
                message = mcp_result.get("message", "Generated via MCP")
                error = None
            else:
                success = False
                file_path = None
                message = mcp_result.get("message", "MCP server error")
                error = message
            
            return {
                "success": success,
                "code": generated_code,
                "file_path": file_path,
                "message": message,
                "error": error if not success else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "code": None,
                "file_path": None,
                "message": f"Error: {str(e)}",
                "error": str(e)
            }
    
    async def interactive_mode(self):
        """Interactive mode for generating diagrams from prompts"""
        print("🚀 AI AWS Diagram Generator - MCP Client Mode")
        print("=" * 70)
        print("Uses MCP protocol to communicate with AWS Diagram Server")
        print("Enter natural language descriptions to generate AWS diagrams")
        print("Type 'quit' or 'exit' to stop")
        print("Type 'examples' to see example prompts")
        print("=" * 70)
        
        while True:
            try:
                prompt = input("\n💬 Describe your AWS architecture: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if prompt.lower() == 'examples':
                    self._show_example_prompts()
                    continue
                
                if not prompt:
                    continue
                
                # Generate filename from prompt
                filename_base = re.sub(r'[^a-zA-Z0-9\s]', '', prompt.lower())
                filename_base = '_'.join(filename_base.split()[:4])
                filename = f"mcp_ai_{filename_base}" if filename_base else "mcp_ai_diagram"
                
                # Generate diagram
                result = await self.generate_diagram_from_prompt(prompt, filename)
                
                if result["success"]:
                    print(f"\n✅ Diagram generated successfully!")
                    print(f"📁 File: {result['file_path']}")
                    if result['file_path'] and os.path.exists(result['file_path']):
                        size = os.path.getsize(result['file_path'])
                        print(f"📏 Size: {size:,} bytes")
                else:
                    print(f"\n❌ Generation failed: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_example_prompts(self):
        """Show example prompts"""
        examples = [
            "A simple web application with load balancer and database",
            "Microservices architecture with API Gateway and DynamoDB",
            "Data pipeline with S3, Lambda, and Redshift",
            "Serverless application with API Gateway and RDS",
            "3-tier architecture with load balancer, EC2, and RDS",
            "Container-based microservices with ECS and ALB",
            "Real-time analytics with Kinesis and ElasticSearch",
            "Machine learning pipeline with SageMaker and S3"
        ]
        
        print("\n📋 Example AWS Architecture Prompts:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")


async def main():
    """Main function"""
    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("❌ AWS credentials not set. Set them with:")
        print("export AWS_ACCESS_KEY_ID='your-access-key'")
        print("export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print("export AWS_REGION='us-west-2'")
        return
    
    # Show configuration
    region = os.getenv('AWS_REGION', 'us-west-2')
    model = os.getenv('ANTHROPIC_MODEL', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
    print(f"🔧 Configuration:")
    print(f"   Region: {region}")
    print(f"   Model: {model}")
    print(f"   MCP Server: AWS Diagram MCP Server")
    print()
    
    try:
        generator = MCPAIDiagramGenerator()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            # Single prompt mode
            prompt = ' '.join(sys.argv[1:])
            result = await generator.generate_diagram_from_prompt(prompt)
            
            if result["success"]:
                print(f"✅ Diagram generated: {result['file_path']}")
            else:
                print(f"❌ Failed: {result['error']}")
        else:
            # Interactive mode
            await generator.interactive_mode()
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())