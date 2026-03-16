"""
Chapter 1-3: 주요 파라미터 이해

API 호출 시 사용하는 주요 파라미터를 실험합니다.
- max_tokens: 최대 출력 토큰 수
- temperature: 응답의 창의성/무작위성 조절 (0.0 ~ 1.0)
- top_p, top_k: 토큰 샘플링 방식
"""

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


def call_claude(prompt: str, temperature: float = 1.0, max_tokens: int = 1024) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# --- 실험 1: max_tokens 제한 ---
print("=== max_tokens 실험 ===")
print("\n[max_tokens=50]")
print(call_claude("Python의 장점 5가지를 설명해주세요.", max_tokens=50))

print("\n[max_tokens=500]")
print(call_claude("Python의 장점 5가지를 설명해주세요.", max_tokens=500))

# --- 실험 2: temperature 비교 ---
# temperature=0.0 → 결정적(deterministic), 항상 같은 응답
# temperature=1.0 → 더 창의적이고 다양한 응답
print("\n=== temperature 실험 ===")

creative_prompt = "'인공지능'을 주제로 한 줄 시를 써주세요."

print("\n[temperature=0.0] 동일 프롬프트 3회 호출:")
for i in range(3):
    result = call_claude(creative_prompt, temperature=0.0, max_tokens=100)
    print(f"  {i + 1}: {result}")

print("\n[temperature=1.0] 동일 프롬프트 3회 호출:")
for i in range(3):
    result = call_claude(creative_prompt, temperature=1.0, max_tokens=100)
    print(f"  {i + 1}: {result}")
