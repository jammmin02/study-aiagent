"""
Chapter 1-5: LLM은 기억하지 못한다 → Agent의 필요성

LLM API는 호출할 때마다 독립적입니다 (stateless).
이전 대화를 기억하지 못하기 때문에, 대화 맥락을 유지하려면
우리가 직접 메시지 히스토리를 관리해야 합니다.

이것이 바로 "Agent"의 가장 기본적인 출발점입니다.
Agent = LLM + 메모리(대화 히스토리) + 루프
"""

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

# ============================================================
# 1부: LLM은 기억하지 못한다 (Stateless)
# ============================================================
print("=" * 60)
print("1부: LLM은 기억하지 못한다")
print("=" * 60)

# 첫 번째 호출: 이름을 알려줌
response1 = client.messages.create(
    model=MODEL,
    max_tokens=256,
    messages=[
        {"role": "user", "content": "내 이름은 영찬이야. 기억해줘!"}
    ],
)
print(f"[1번 호출] 사용자: 내 이름은 영찬이야. 기억해줘!")
print(f"[1번 호출] Claude: {response1.content[0].text}")

# 두 번째 호출: 이름을 물어봄 → 기억하지 못함!
# 이전 호출과 완전히 독립적인 새로운 요청이기 때문
response2 = client.messages.create(
    model=MODEL,
    max_tokens=256,
    messages=[
        {"role": "user", "content": "내 이름이 뭐였지?"}
    ],
)
print(f"\n[2번 호출] 사용자: 내 이름이 뭐였지?")
print(f"[2번 호출] Claude: {response2.content[0].text}")
# → 모른다고 답하거나 엉뚱한 이름을 말할 것

# ============================================================
# 2부: 메시지 히스토리로 기억 만들기
# ============================================================
# 해결책: 이전 대화 내용을 messages에 포함시켜 보내면 됩니다.
# LLM이 "기억"하는 것이 아니라, 매번 전체 대화를 다시 읽는 것입니다.
print()
print("=" * 60)
print("2부: 메시지 히스토리로 기억 만들기")
print("=" * 60)

response3 = client.messages.create(
    model=MODEL,
    max_tokens=256,
    messages=[
        # 1번 호출의 대화 내용을 포함
        {"role": "user", "content": "내 이름은 영찬이야. 기억해줘!"},
        {"role": "assistant", "content": response1.content[0].text},
        # 그 위에 새로운 질문 추가
        {"role": "user", "content": "내 이름이 뭐였지?"},
    ],
)
print(f"[히스토리 포함] 사용자: 내 이름이 뭐였지?")
print(f"[히스토리 포함] Claude: {response3.content[0].text}")
# → 이번에는 "영찬"이라고 올바르게 답할 것

# ============================================================
# 3부: 간단한 Agent 루프
# ============================================================
# 위 패턴을 자동화하면 → Agent의 기본 구조가 됩니다.
#
#   Agent = while 루프 + 메시지 히스토리 + LLM 호출
#
#   [사용자 입력] → [히스토리에 추가] → [LLM 호출] → [응답을 히스토리에 추가] → 반복
print()
print("=" * 60)
print("3부: 간단한 Agent 루프 (종료하려면 'quit' 입력)")
print("=" * 60)

conversation_history = []  # 대화 히스토리를 저장할 리스트

while True:
    user_input = input("\n사용자: ")
    if user_input.strip().lower() == "quit":
        print("대화를 종료합니다.")
        break

    # 사용자 메시지를 히스토리에 추가
    conversation_history.append({"role": "user", "content": user_input})

    # 전체 히스토리를 포함하여 LLM 호출
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=conversation_history,  # 누적된 전체 대화를 매번 전송
    )

    assistant_message = response.content[0].text

    # AI 응답도 히스토리에 추가 → 다음 호출에서 맥락 유지
    conversation_history.append({"role": "assistant", "content": assistant_message})

    print(f"Claude: {assistant_message}")

    # 현재 히스토리 크기 표시 (토큰이 계속 누적됨을 보여줌)
    print(f"  [히스토리: {len(conversation_history)}개 메시지, "
          f"토큰 사용: 입력 {response.usage.input_tokens} / 출력 {response.usage.output_tokens}]")
