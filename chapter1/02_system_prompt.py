"""
Chapter 1-2: System Prompt 활용

System prompt로 AI의 역할과 행동 방식을 지정합니다.
- system 파라미터의 역할
- 동일한 질문, 다른 system prompt → 다른 응답
"""

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

user_message = "Python에서 리스트와 튜플의 차이가 뭐야?"

# --- 예시 1: system prompt 없이 ---
print("=== System Prompt 없음 ===")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": user_message}],
)
print(response.content[0].text)

# --- 예시 2: 친절한 한국어 선생님 ---
print("\n=== 친절한 선생님 역할 ===")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="당신은 프로그래밍을 처음 배우는 학생을 가르치는 친절한 선생님입니다. 비유를 들어 쉽게 설명하세요.",
    messages=[{"role": "user", "content": user_message}],
)
print(response.content[0].text)

# --- 예시 3: 시니어 개발자 ---
print("\n=== 시니어 개발자 역할 ===")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="당신은 10년차 시니어 Python 개발자입니다. 기술적으로 정확하고 간결하게 답변하되, 실무에서의 best practice를 함께 알려주세요.",
    messages=[{"role": "user", "content": user_message}],
)
print(response.content[0].text)

