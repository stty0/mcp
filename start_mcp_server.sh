#!/bin/bash
# MCP Server Startup Script for AWS Diagram Generator

echo "🚀 Starting AWS Diagram MCP Server..."

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Set working directory
cd /home/jrpark/workspace/mcp/src/scp-diagram-mcp-server

# Start the MCP server
echo "📡 Server running on stdio (MCP protocol)"
echo "Use Ctrl+C to stop the server"

# Run the server
uv run python -m server