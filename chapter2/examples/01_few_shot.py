"""
Chapter 2-1: Few-shot Prompting (In-context Learning)

In-context Learning이란?
  모델을 재학습(fine-tuning)하지 않고, 프롬프트 안에 예시를 넣는 것만으로
  모델의 행동을 유도하는 기법입니다.
  모델의 가중치(weights)는 변하지 않습니다 — 입력 문맥(context)만으로 원하는 출력을 이끌어냅니다.

예시 개수에 따른 분류:
  - Zero-shot: 예시 없이 지시만 (예: "감성을 분류하세요")
  - One-shot: 예시 1개를 함께 제공
  - Few-shot: 예시 2~5개를 함께 제공

주의:
  "학습"이라는 표현이 붙지만, 모델이 실제로 학습하는 것은 아닙니다.
  매번 호출할 때마다 예시를 함께 보내야 동일한 효과를 얻을 수 있습니다.

Agent에서의 활용:
  입력 → 출력 패턴을 예시로 정의하면, 별도 파싱 로직 없이도
  LLM이 일관된 형식으로 응답하게 만들 수 있습니다.
"""

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"


# ============================================================
# 1부: Zero-shot vs Few-shot 비교
# ============================================================
# 같은 작업(감성 분류)을 예시 유무에 따라 비교합니다.

print("=" * 60)
print("1부: Zero-shot vs Few-shot 비교")
print("=" * 60)

target_text = "배송이 하루만에 왔는데 포장이 찢어져 있었어요"

# --- Zero-shot: 지시만 ---
print("\n--- Zero-shot ---")
response = client.messages.create(
    model=MODEL,
    max_tokens=100,
    messages=[{
        "role": "user",
        "content": f"다음 리뷰의 감성을 '긍정', '부정', '혼합' 중 하나로 분류하세요.\n\n리뷰: {target_text}",
    }],
)
print(f"응답: {response.content[0].text}")
# → 정답을 맞출 수는 있지만, "혼합입니다. 왜냐하면..." 같은 긴 설명이 붙을 수 있음
# → 출력 형식이 일정하지 않아 프로그래밍에서 파싱하기 어려움

# --- Few-shot: 예시를 함께 제공 ---
# user/assistant 메시지 쌍으로 "이런 입력에는 이렇게 답해"라는 패턴을 보여줍니다.
# LLM은 이 패턴을 따라하여 마지막 질문에도 동일한 형식으로 응답합니다.
print("\n--- Few-shot ---")
response = client.messages.create(
    model=MODEL,
    max_tokens=100,
    messages=[
        # 예시 1: 긍정
        {"role": "user", "content": "리뷰: 정말 좋은 제품이에요! 추천합니다."},
        {"role": "assistant", "content": "긍정"},
        # 예시 2: 부정
        {"role": "user", "content": "리뷰: 품질이 너무 안 좋고 환불도 어렵네요."},
        {"role": "assistant", "content": "부정"},
        # 예시 3: 혼합
        {"role": "user", "content": "리뷰: 기능은 좋은데 가격이 너무 비싸요."},
        {"role": "assistant", "content": "혼합"},
        # 실제 분류 대상
        {"role": "user", "content": f"리뷰: {target_text}"},
    ],
)
print(f"응답: {response.content[0].text}")
# → "혼합" 한 단어로 일관되게 응답


# ============================================================
# 2부: Few-shot으로 출력 형식 통제
# ============================================================
# "키워드를 추출해줘"라고만 하면 모델마다, 호출마다 형식이 달라질 수 있습니다.
# 예시를 통해 "#태그 #형식"이라는 출력 패턴을 보여주면, 일관된 형식을 얻을 수 있습니다.
print()
print("=" * 60)
print("2부: Few-shot으로 출력 형식 통제")
print("=" * 60)

print("\n--- 키워드 추출 (태그 형식) ---")
response = client.messages.create(
    model=MODEL,
    max_tokens=100,
    messages=[
        # 예시 1
        {"role": "user", "content": "텍스트: 오늘 서울에 폭우가 내려 지하철 운행이 지연되고 있습니다."},
        {"role": "assistant", "content": "#서울 #폭우 #지하철 #운행지연"},
        # 예시 2
        {"role": "user", "content": "텍스트: 삼성전자가 신형 갤럭시를 출시하며 AI 기능을 대폭 강화했다."},
        {"role": "assistant", "content": "#삼성전자 #갤럭시 #출시 #AI"},
        # 실제 추출 대상
        {"role": "user", "content": "텍스트: 정부가 내년도 교육 예산을 늘려 초등학교 코딩 교육을 의무화한다."},
    ],
)
print(f"응답: {response.content[0].text}")
# → "#정부 #교육 #예산 #코딩 #의무화" 형식으로 응답


# ============================================================
# 3부: Few-shot + System Prompt 조합
# ============================================================
# System Prompt → "무엇을 하는 AI인지" 역할과 규칙을 정의
# Few-shot → "어떤 형식으로 답할지" 구체적 입출력 패턴을 시연
# 두 가지를 조합하면 가장 안정적인 출력을 얻을 수 있습니다.
print()
print("=" * 60)
print("3부: System Prompt + Few-shot 조합")
print("=" * 60)

print("\n--- SQL 쿼리 생성기 ---")
response = client.messages.create(
    model=MODEL,
    max_tokens=200,
    system="""당신은 자연어를 SQL 쿼리로 변환하는 변환기입니다.
테이블: users (id, name, age, city, created_at)
SQL 쿼리만 출력하세요. 설명은 하지 마세요.""",
    messages=[
        # 예시 1
        {"role": "user", "content": "서울에 사는 사용자 목록"},
        {"role": "assistant", "content": "SELECT * FROM users WHERE city = '서울';"},
        # 예시 2
        {"role": "user", "content": "30살 이상 사용자 수"},
        {"role": "assistant", "content": "SELECT COUNT(*) FROM users WHERE age >= 30;"},
        # 실제 변환 대상
        {"role": "user", "content": "최근 가입한 부산 사용자 5명"},
    ],
)
print(f"응답: {response.content[0].text}")


# ============================================================
# 정리: Few-shot Prompting 핵심
# ============================================================
print()
print("=" * 60)
print("정리: Few-shot Prompting 핵심")
print("=" * 60)
print("""
1. 예시 개수 가이드
   - Zero-shot: 간단한 작업, LLM이 이미 잘 아는 경우
   - 1~2개: 출력 형식을 맞추고 싶을 때
   - 3~5개: 패턴이 복잡하거나 일관성이 중요할 때
   - 너무 많으면 토큰 낭비 → 적절한 균형 필요

2. 좋은 예시의 조건
   - 실제 사용 케이스와 유사할 것
   - 다양한 케이스를 커버할 것 (긍정/부정/혼합 모두 포함)
   - 출력 형식이 일관될 것

3. 주의사항
   - Few-shot은 "학습"이 아닙니다 — 매 호출마다 예시를 포함해야 합니다
   - 예시가 많을수록 input 토큰이 늘어나 비용이 증가합니다
   - 구조화된 출력이 필요하면 Ch1-8의 Structured Output도 함께 고려하세요

4. Agent에서의 활용
   - 도구 선택 패턴을 예시로 보여줄 수 있음
   - System Prompt(역할) + Few-shot(형식) = 가장 안정적인 조합
""")
