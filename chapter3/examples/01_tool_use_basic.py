"""
Chapter 3-1: Tool Use 기본

Tool Use(Function Calling)란?
    LLM이 직접 답할 수 없는 질문에 대해,
    "이 도구를 이 인자로 호출해줘"라고 요청하는 메커니즘입니다.

    LLM은 도구를 직접 실행하지 않습니다.
    도구 호출을 "요청"할 뿐이고, 실제 실행은 Agent(우리 코드)가 합니다.

흐름:
    1. 개발자가 사용 가능한 도구 목록을 API에 전달 (tools 파라미터)
    2. LLM이 사용자 질문을 보고, 도구가 필요하면 tool_use 블록을 반환
    3. Agent(우리 코드)가 해당 도구를 실제로 실행
    4. 실행 결과를 tool_result로 LLM에 다시 전달
    5. LLM이 결과를 바탕으로 최종 답변 생성

    [User] → [LLM: "계산기 도구를 써야겠다"] → [Agent: 도구 실행] → [LLM: "답은 42입니다"]
"""

import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"


# ============================================================
# 1부: 도구 정의
# ============================================================
# 도구는 JSON Schema 형식으로 정의합니다.
# LLM은 이 스키마를 읽고, 언제 어떤 인자로 호출할지 스스로 판단합니다.

print("=" * 60)
print("1부: 도구 정의와 기본 호출")
print("=" * 60)

# 간단한 계산기 도구 정의
tools = [
    {
        "name": "calculator",              # 도구 이름 (LLM이 호출 시 사용)
        "description": "두 숫자의 사칙연산을 수행합니다. 수학 계산이 필요할 때 사용하세요.",  # 언제 쓸지 설명
        "input_schema": {                   # 입력 파라미터 정의 (JSON Schema)
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "계산할 수학 표현식 (예: '2 + 3', '10 * 5')",
                },
            },
            "required": ["expression"],     # 필수 파라미터
        },
    }
]

# 도구 정의의 핵심 요소:
#   - name: 도구 식별자. LLM이 호출할 때 이 이름을 사용
#   - description: LLM이 "이 도구를 써야 하나?"를 판단하는 근거
#     → 설명이 명확할수록 LLM이 적절한 시점에 도구를 호출합니다
#   - input_schema: 도구가 받는 인자의 형태 (JSON Schema 표준)
#     → LLM은 이 스키마에 맞게 인자를 생성합니다


# ============================================================
# 2부: 도구가 포함된 API 호출
# ============================================================
# tools 파라미터로 도구를 전달하면, LLM이 필요 시 도구 호출을 요청합니다.
print()
print("=" * 60)
print("2부: LLM의 도구 호출 요청")
print("=" * 60)

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=tools,        # ← 사용 가능한 도구 목록 전달
    messages=[
        {"role": "user", "content": "127 곱하기 389는 얼마야?"}
    ],
)

# 응답 구조 확인
print("\n[응답 전체 구조]")
print(f"stop_reason: {response.stop_reason}")  # "tool_use" ← 도구 호출을 위해 중단됨!
print(f"content 블록 수: {len(response.content)}")

for i, block in enumerate(response.content):
    print(f"\n  [블록 {i}] type: {block.type}")
    if block.type == "text":
        print(f"    text: {block.text}")
    elif block.type == "tool_use":
        print(f"    id: {block.id}")           # 도구 호출 고유 ID (결과 반환 시 필요)
        print(f"    name: {block.name}")        # 호출할 도구 이름
        print(f"    input: {block.input}")      # 도구에 전달할 인자

# stop_reason이 "tool_use"라는 것은:
#   LLM이 "나는 여기서 멈출게, 이 도구를 실행해서 결과를 알려줘"라고 한 것입니다.


# ============================================================
# 3부: 도구 실행 → 결과 반환 → 최종 답변
# ============================================================
# 전체 흐름을 하나로 연결합니다.
print()
print("=" * 60)
print("3부: 전체 흐름 (요청 → 도구 실행 → 최종 답변)")
print("=" * 60)


def run_calculator(expression: str) -> str:
    """계산기 도구의 실제 구현"""
    try:
        # 주의: eval은 보안 위험이 있으므로 학습용으로만 사용
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"계산 오류: {e}"


# Step 1: 사용자 질문 + 도구 정의로 API 호출
print("\n[Step 1] 사용자 질문 전송")
messages = [
    {"role": "user", "content": "127 곱하기 389는 얼마야?"}
]

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=tools,
    messages=messages,
)
print(f"  stop_reason: {response.stop_reason}")

# Step 2: LLM이 도구 호출을 요청했는지 확인하고 실행
if response.stop_reason == "tool_use":
    # tool_use 블록 찾기
    tool_block = next(b for b in response.content if b.type == "tool_use")

    print(f"\n[Step 2] LLM이 도구 호출 요청")
    print(f"  도구: {tool_block.name}")
    print(f"  인자: {tool_block.input}")

    # 도구 실제 실행
    tool_result = run_calculator(tool_block.input["expression"])
    print(f"  실행 결과: {tool_result}")

    # Step 3: 도구 결과를 LLM에 반환
    # messages에 LLM의 응답(tool_use)과 도구 결과(tool_result)를 추가
    print(f"\n[Step 3] 도구 결과를 LLM에 전달")
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_block.id,   # 어떤 도구 호출에 대한 결과인지 매칭
                "content": tool_result,
            }
        ],
    })

    # Step 4: LLM이 도구 결과를 보고 최종 답변 생성
    final_response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )
    print(f"\n[Step 4] 최종 답변")
    print(f"  stop_reason: {final_response.stop_reason}")  # "end_turn"
    print(f"  답변: {final_response.content[0].text}")


# ============================================================
# 정리: Tool Use 메시지 흐름
# ============================================================
print()
print("=" * 60)
print("정리: Tool Use 메시지 흐름")
print("=" * 60)
print("""
[전체 흐름]

  User: "127 × 389는?"
    │
    ▼
  LLM 호출 (tools 포함)
    │
    ▼
  LLM 응답: stop_reason="tool_use"
    content: [
      TextBlock("계산해보겠습니다"),
      ToolUseBlock(name="calculator", input={"expression": "127 * 389"})
    ]
    │
    ▼
  Agent가 도구 실행: eval("127 * 389") → "49403"
    │
    ▼
  LLM 재호출 (tool_result 포함)
    messages: [...이전 대화, tool_result: "49403"]
    │
    ▼
  LLM 최종 응답: stop_reason="end_turn"
    "127 곱하기 389는 49,403입니다."

[핵심 포인트]
1. LLM은 도구를 직접 실행하지 않는다 — "호출 요청"만 한다
2. 도구 실행은 Agent(우리 코드)의 책임이다
3. tool_use_id로 요청과 결과를 매칭한다
4. stop_reason으로 도구 호출 여부를 판단한다
   - "tool_use": 도구 실행이 필요함 → 도구 실행 후 재호출
   - "end_turn": 최종 답변 완료
""")
