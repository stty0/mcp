#!/bin/bash
# MCP Server Startup Script for AWS Diagram Generator

# NOTE: stdout is reserved for the MCP JSON-RPC protocol, so all
# diagnostic messages below are written to stderr.
echo "🚀 Starting AWS Diagram MCP Server..." >&2

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Set working directory
cd /home/jrpark/workspace/mcp/src/scp-diagram-mcp-server

# Generate the SCP icon provider if it's missing (e.g. after a fresh uv sync)
if [ ! -d ".venv/lib64/python3.12/site-packages/diagrams/scp" ] && [ ! -d ".venv/lib/python3.12/site-packages/diagrams/scp" ]; then
    echo "🔧 Generating SCP icon provider..." >&2
    uv run python scripts/generate_scp_provider.py >&2
fi

# Start the MCP server
echo "📡 Server running on stdio (MCP protocol)" >&2
echo "Use Ctrl+C to stop the server" >&2

# Run the server
uv run python -m server