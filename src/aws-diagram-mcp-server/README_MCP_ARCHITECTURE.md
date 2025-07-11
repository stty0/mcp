# AWS Diagram Generator - MCP Server-Client Architecture

## 🏗️ 아키텍처 구조

```
┌─────────────────────┐    MCP Protocol    ┌─────────────────────┐
│                     │ ◄────────────────► │                     │
│   MCP AI Client     │     (stdio)        │   AWS Diagram       │
│                     │                    │   MCP Server        │
│ - Bedrock Claude    │                    │                     │
│ - Natural Language  │                    │ - Icon Discovery    │
│ - Interactive Mode  │                    │ - Code Generation   │
│                     │                    │ - Diagram Export    │
└─────────────────────┘                    └─────────────────────┘
```

## 📁 파일 구조

### 서버 측
- `awslabs/aws_diagram_mcp_server/` - MCP 서버 구현
- `start_mcp_server.sh` - 서버 시작 스크립트

### 클라이언트 측  
- `mcp_ai_client.py` - AI 기반 MCP 클라이언트 (추천)
- `simple_client.py` - 기본 MCP 클라이언트
- `working_client.py` - 직접 호출 클라이언트 (구버전)

## 🚀 사용 방법

### 1. 환경 설정
```bash
# AWS 자격 증명 및 Bedrock 설정
source setup_bedrock.sh
```

### 2. MCP 서버-클라이언트 모드 (권장)

**대화형 모드:**
```bash
uv run python mcp_ai_client.py
```

**명령행 모드:**
```bash
uv run python mcp_ai_client.py "A web app with load balancer and database"
```

### 3. 서버 별도 실행 (선택사항)
```bash
# 터미널 1: 서버 시작
./start_mcp_server.sh

# 터미널 2: 클라이언트 연결
uv run python simple_client.py
```

## ✨ 주요 기능

### MCP AI Client (`mcp_ai_client.py`)
- ✅ AWS Bedrock Claude Sonnet 4 통합
- ✅ MCP 프로토콜을 통한 서버 통신
- ✅ 자연어 프롬프트 → AWS 다이어그램
- ✅ 대화형 모드 지원
- ✅ 자동 파일명 생성

### MCP Server Features
- ✅ 3개 도구: `list_icons`, `get_diagram_examples`, `generate_diagram`
- ✅ 20개 클라우드 프로바이더 지원
- ✅ 보안 코드 스캐닝
- ✅ PNG 다이어그램 생성

## 🔧 기술 스택

- **AI**: AWS Bedrock Claude Sonnet 4
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: stdio (JSON-RPC)
- **Diagrams**: Python diagrams package
- **Output**: PNG files

## 📊 테스트 결과

```
✅ Bedrock 연결: 성공
✅ MCP 서버 통신: 성공  
✅ 다이어그램 생성: 성공
📁 Generated: diagram_e97e7586.png
```

## 🎯 예제 프롬프트

1. "A simple web application with load balancer and database"
2. "Microservices with API Gateway, Lambda, and DynamoDB" 
3. "Data pipeline with S3, Lambda, and Redshift"
4. "Serverless application with API Gateway and RDS"

## 🔍 디버깅

**MCP 통신 확인:**
```bash
# 서버 로그 확인
FASTMCP_LOG_LEVEL=DEBUG uv run python mcp_ai_client.py
```

**생성된 다이어그램 확인:**
```bash
ls -la generated-diagrams/
```

## 🎉 장점

1. **분리된 아키텍처**: 서버와 클라이언트 독립 실행
2. **표준 프로토콜**: MCP를 통한 안정적 통신
3. **AI 통합**: 자연어로 다이어그램 생성
4. **확장성**: 다른 클라이언트 쉽게 추가 가능
5. **재사용성**: MCP 서버를 다른 용도로도 활용