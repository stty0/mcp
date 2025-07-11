# AWS Diagram MCP Server - Python Client

이 프로젝트는 AWS Diagram MCP Server와 통신하는 Python 클라이언트를 제공합니다.

## 파일 구성

- `simple_client.py` - MCP 라이브러리를 사용한 간단한 클라이언트 (권장)
- `mcp_client.py` - 저수준 JSON-RPC 클라이언트 (참고용)
- `requirements-client.txt` - 클라이언트 의존성

## 사전 준비

1. **uv 설치**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **MCP 서버 설치 확인**:
   ```bash
   uvx awslabs.aws-diagram-mcp-server
   ```

## 사용법

### 1. 간단한 테스트 실행

```bash
# uv 환경에서 실행
uv run python simple_client.py
```

### 2. 프로그래밍 방식 사용

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def generate_diagram():
    server_params = StdioServerParameters(
        command="uvx",
        args=["awslabs.aws-diagram-mcp-server"],
        env={"FASTMCP_LOG_LEVEL": "ERROR"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 다이어그램 코드
            code = '''
with Diagram("My Architecture", show=False):
    user = Generic("User")
    lb = ELB("Load Balancer")
    web = EC2("Web Server")
    db = RDS("Database")
    
    user >> lb >> web >> db
'''
            
            # 다이어그램 생성
            result = await session.call_tool("generate_diagram", {
                "code": code,
                "filename": "my_architecture",
                "workspace_dir": "/path/to/workspace"
            })
            
            print(result.content[0].text)

# 실행
asyncio.run(generate_diagram())
```

## 사용 가능한 도구

### 1. `list_icons`
사용 가능한 아이콘 목록을 조회합니다.

```python
# 모든 제공자 조회
await session.call_tool("list_icons", {})

# AWS 서비스 조회
await session.call_tool("list_icons", {"provider_filter": "aws"})

# AWS 컴퓨팅 아이콘 조회
await session.call_tool("list_icons", {
    "provider_filter": "aws", 
    "service_filter": "compute"
})
```

### 2. `get_diagram_examples`
다이어그램 예제 코드를 가져옵니다.

```python
# AWS 예제
await session.call_tool("get_diagram_examples", {"diagram_type": "aws"})

# 모든 예제
await session.call_tool("get_diagram_examples", {"diagram_type": "all"})
```

### 3. `generate_diagram`
Python 코드로 다이어그램을 생성합니다.

```python
await session.call_tool("generate_diagram", {
    "code": "with Diagram('Test', show=False): ELB('lb') >> EC2('web')",
    "filename": "test_diagram",
    "workspace_dir": "/current/directory",
    "timeout": 90
})
```

## 트러블슈팅

### 1. uvx 명령어를 찾을 수 없음
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 2. MCP 라이브러리 설치
```bash
uv pip install mcp
```

### 3. 권한 오류
현재 작업 디렉토리에 쓰기 권한이 있는지 확인하세요.

## 예제 출력

성공적인 다이어그램 생성 시:
```json
{
  "content": {
    "success": true,
    "file_path": "/path/to/generated-diagrams/my_diagram.png",
    "message": "Diagram generated successfully"
  }
}
```

## 개발 팁

1. **디버깅**: `FASTMCP_LOG_LEVEL=DEBUG`로 설정하여 자세한 로그 확인
2. **타임아웃**: 복잡한 다이어그램의 경우 `timeout` 값을 늘려주세요
3. **경로**: `workspace_dir`를 항상 명시하여 파일 저장 위치를 확실히 하세요