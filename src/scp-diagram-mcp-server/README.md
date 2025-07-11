# SCP Diagram MCP Server

An MCP server that seamlessly creates diagrams using the Python diagrams package DSL.

## Features

- Generate professional AWS architecture diagrams
- Support for multiple diagram types (AWS, sequence, flow, etc.)
- List available icons and services
- Get diagram examples and templates
- Direct Python code execution for diagram generation

## Installation

```bash
uv pip install -e .
```

## Usage

### As MCP Server

```bash
uv run python -m server
```

### Direct Usage

```python
from diagrams_tools import generate_diagram

result = await generate_diagram(
    code="with Diagram('Web Service', show=False): ELB('lb') >> EC2('web')",
    filename="my_diagram"
)
```

## License

Apache-2.0