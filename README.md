# 글로벌시스템융합과 AI-Agent 교과목 실습자료

Claude API를 활용한 AI Agent 개발 실습 코드 모음입니다.
LLM과의 기본 통신부터 시작하여 Agent를 단계적으로 구축해나갑니다.

## 사전 준비

### 1. Python 환경

- Python 3.13 이상

### 2. 의존성 설치

```bash
pip install -e .
```

### 3. API 키 설정

프로젝트 루트에 `.env` 파일을 생성하고 수업시간에 배부된 API 키를 입력합니다.

```
ANTHROPIC_API_KEY=수업시간에_배부된_키
```

## 실습 목차

### Chapter 1: LLM 기본 통신

AI Agent와 LLM 사이의 기본적인 통신 방법을 배웁니다.

| 파일 | 주제 | 핵심 내용 |
|------|------|-----------|
| `01_basic_call.py` | API 기본 호출 | 클라이언트 생성, `messages.create()`, 응답 구조, 토큰 개념 |
| `02_system_prompt.py` | System Prompt | `system` 파라미터로 AI의 역할과 행동 방식 지정 |
| `03_parameters.py` | 주요 파라미터 | `max_tokens`, `temperature` 실험 |
| `04_streaming.py` | 스트리밍 응답 | 실시간 토큰 수신, 이벤트 타입별 처리 |
| `05_stateless_and_agent.py` | Stateless → Agent | LLM의 무상태 특성, 대화 히스토리 관리, Agent 루프 |
| `06_message_format.py` | 메시지 포맷 | 요청/응답의 실제 구조, 멀티턴 메시지 흐름 |
| `07_error_handling.py` | 에러 핸들링 | 에러 타입별 처리, Exponential Backoff 재시도 |

### 실행 방법

```bash
python chapter1/01_basic_call.py
```

## 기술 스택

- **LLM**: Claude API (Anthropic)
- **언어**: Python 3.13+
- **주요 라이브러리**: `anthropic`, `python-dotenv`
