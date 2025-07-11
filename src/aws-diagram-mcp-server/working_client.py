#!/usr/bin/env python3
"""
AI-Powered AWS Diagram Generator

Uses AWS Bedrock Claude Sonnet 4 to generate AWS diagrams from natural language prompts
"""

import asyncio
import os
import sys
import json
import re
from typing import Optional

# Add server path for direct testing
sys.path.insert(0, '/home/jrpark/workspace/mcp/src/aws-diagram-mcp-server')

from awslabs.aws_diagram_mcp_server.diagrams_tools import (
    generate_diagram,
    get_diagram_examples, 
    list_diagram_icons,
)
from awslabs.aws_diagram_mcp_server.models import DiagramType

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("❌ Boto3 library not found. Install it with:")
    print("pip install boto3")
    sys.exit(1)


class AIAwsDiagramGenerator:
    """AI-powered AWS diagram generator using AWS Bedrock Claude Sonnet 4"""
    
    def __init__(self, region: Optional[str] = None, workspace_dir: Optional[str] = None):
        """
        Initialize the AI diagram generator
        
        Args:
            region: AWS region (if not provided, will use AWS_REGION env var or us-west-2)
            workspace_dir: Directory to save diagrams (defaults to current directory)
        """
        self.region = region or os.getenv('AWS_REGION', 'us-west-2')
        self.model_id = os.getenv('ANTHROPIC_MODEL', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
        
        try:
            # Initialize Bedrock client
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
        
        self.workspace_dir = workspace_dir or os.getcwd()
        
        # Cache for available icons and examples
        self._providers_cache = None
        self._aws_services_cache = None
        self._examples_cache = None
    
    def _test_bedrock_connection(self):
        """Test Bedrock connection and model access"""
        try:
            # Simple test request
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
    
    async def _get_available_icons(self, provider="aws", service=None):
        """Get available icons for context"""
        if provider == "aws" and not self._aws_services_cache:
            result = list_diagram_icons("aws", None)
            self._aws_services_cache = result.providers.get("aws", {})
        
        if service:
            result = list_diagram_icons(provider, service)
            provider_data = result.providers.get(provider, {})
            return provider_data.get(service, [])
        
        return self._aws_services_cache or {}
    
    async def _get_examples(self):
        """Get diagram examples for context"""
        if not self._examples_cache:
            result = get_diagram_examples(DiagramType.AWS)
            self._examples_cache = result.examples
        return self._examples_cache
    
    def _build_context_prompt(self, aws_services, examples):
        """Build context prompt with available icons and examples"""
        
        # Sample of available AWS services
        service_sample = list(aws_services.keys())[:15]
        
        # Sample icons from compute and database services
        compute_icons = aws_services.get('compute', [])[:10]
        database_icons = aws_services.get('database', [])[:8]
        network_icons = aws_services.get('network', [])[:8]
        
        # Sample examples
        example_names = list(examples.keys())[:3]
        example_code = []
        for name in example_names:
            code = examples[name]
            example_code.append(f"# {name}\n{code}")
        
        context = f"""
You are an AWS diagram code generator. Generate Python code using the diagrams package to create AWS architecture diagrams.

AVAILABLE AWS SERVICES (sample):
{', '.join(service_sample)}

AVAILABLE ICONS (samples):
- Compute: {', '.join(compute_icons)}
- Database: {', '.join(database_icons)}  
- Network: {', '.join(network_icons)}

EXAMPLE PATTERNS:
{chr(10).join(example_code[:2])}

IMPORTANT RULES:
1. Always start with: with Diagram("Title", show=False):
2. Use only available AWS icons (case-sensitive)
3. Use >> for connections: service1 >> service2
4. Use Cluster for grouping: with Cluster("name"):
5. Use direction="LR" or "TB" for layout
6. NO IMPORTS needed - all icons are pre-imported
7. Keep it simple and focused

RESPONSE FORMAT:
Return ONLY the Python code, no explanations or markdown.
"""
        return context
    
    async def generate_diagram_from_prompt(self, user_prompt: str, filename: Optional[str] = None) -> dict:
        """
        Generate AWS diagram from natural language prompt
        
        Args:
            user_prompt: Natural language description of the architecture
            filename: Optional filename for the diagram
            
        Returns:
            Dictionary with generation result
        """
        try:
            print(f"🤖 Processing prompt: {user_prompt}")
            
            # Get context
            aws_services = await self._get_available_icons("aws")
            examples = await self._get_examples()
            
            # Build context prompt
            context = self._build_context_prompt(aws_services, examples)
            
            # Generate code using Bedrock Claude
            print(f"🧠 Generating diagram code with Bedrock Claude Sonnet 4...")
            
            # Prepare Bedrock request
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
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(bedrock_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            generated_code = response_body['content'][0]['text'].strip()
            
            # Clean up code (remove markdown formatting if present)
            if "```python" in generated_code:
                generated_code = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
                if generated_code:
                    generated_code = generated_code.group(1)
            elif "```" in generated_code:
                generated_code = re.search(r'```\n(.*?)\n```', generated_code, re.DOTALL)
                if generated_code:
                    generated_code = generated_code.group(1)
            
            print("📝 Generated code:")
            print("=" * 50)
            print(generated_code)
            print("=" * 50)
            
            # Generate diagram
            print("🎨 Creating diagram...")
            result = await generate_diagram(
                code=generated_code,
                filename=filename,
                timeout=90,
                workspace_dir=self.workspace_dir
            )
            
            return {
                "success": result.status == "success",
                "code": generated_code,
                "file_path": result.path if result.status == "success" else None,
                "message": result.message,
                "error": result.message if result.status != "success" else None
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
        print("🚀 AI AWS Diagram Generator - Interactive Mode (Bedrock)")
        print("=" * 70)
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
                filename = f"ai_generated_{filename_base}" if filename_base else "ai_generated_diagram"
                
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
            "A simple web application with load balancer, web servers, and database",
            "Microservices architecture with API Gateway, Lambda functions, and DynamoDB",
            "Data pipeline with S3, Lambda, Kinesis, and Redshift",
            "CI/CD pipeline with CodeCommit, CodeBuild, and CodeDeploy",
            "Serverless application with API Gateway, Lambda, and RDS",
            "Multi-tier web application with Auto Scaling and CloudFront",
            "Event-driven architecture with SQS, SNS, and Lambda",
            "Container orchestration with ECS, ALB, and RDS"
        ]
        
        print("\n📋 Example prompts:")
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
    print()
    
    try:
        generator = AIAwsDiagramGenerator()
        
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