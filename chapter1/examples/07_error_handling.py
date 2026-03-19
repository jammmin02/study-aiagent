"""
Chapter 1-7: 에러 핸들링과 재시도

API 호출은 언제든 실패할 수 있습니다.
Agent가 안정적으로 동작하려면 에러를 적절히 처리해야 합니다.
- 주요 에러 타입과 대처법
- 재시도 로직 (Exponential Backoff)
- Agent 루프에 에러 핸들링 적용
"""

import time
from dotenv import load_dotenv
from anthropic import (
    Anthropic,
    APIError,
    AuthenticationError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    NotFoundError,
)

load_dotenv()

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

# Agent 품질 = 모델 성능 × 도구 설계 × 검증 × 재시도 × 관측 가능성
# ============================================================
# 1부: 주요 에러 타입 알아보기
# ============================================================
# API 호출 시 발생할 수 있는 에러들:
#
#   AuthenticationError (401)
#     - API 키가 없거나 잘못된 경우
#     - 해결: .env 파일의 ANTHROPIC_API_KEY 확인
#
#   BadRequestError (400)
#     - 잘못된 파라미터 (예: 존재하지 않는 모델명, 빈 messages)
#     - 해결: 요청 파라미터 수정
#
#   RateLimitError (429)
#     - 너무 많은 요청을 보냈을 때 (분당/일당 제한 초과)
#     - 해결: 잠시 대기 후 재시도
#
#   APITimeoutError
#     - 응답이 너무 오래 걸릴 때
#     - 해결: timeout 늘리기 또는 재시도
#
#   APIError (500, 529 등)
#     - 서버 측 일시적 오류 또는 과부하
#     - 해결: 잠시 대기 후 재시도

print("=" * 60)
print("1부: 에러 타입별 처리")
print("=" * 60)


# --- 예시 1: 잘못된 모델명 → BadRequestError ---
print("\n--- 잘못된 모델명으로 호출 ---")
try:
    response = client.messages.create(
        model="claude-nonexistent-model",  # 존재하지 않는 모델
        max_tokens=100,
        messages=[{"role": "user", "content": "안녕"}],
    )
except NotFoundError as e:
    # 존재하지 않는 모델명은 404 NotFoundError를 발생시킴
    print(f"[NotFoundError] 상태 코드: {e.status_code}")
    print(f"[NotFoundError] 메시지: {e.message}")
except BadRequestError as e:
    print(f"[BadRequestError] 상태 코드: {e.status_code}")
    print(f"[BadRequestError] 메시지: {e.message}")


# --- 예시 2: 빈 메시지 → BadRequestError ---
print("\n--- 빈 메시지로 호출 ---")
try:
    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[],  # 빈 리스트
    )
except BadRequestError as e:
    print(f"[BadRequestError] {e.message}")


# --- 예시 3: 잘못된 API 키 → AuthenticationError ---
print("\n--- 잘못된 API 키로 호출 ---")
bad_client = Anthropic(api_key="sk-ant-invalid-key-12345")
try:
    response = bad_client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": "안녕"}],
    )
except AuthenticationError as e:
    print(f"[AuthenticationError] 상태 코드: {e.status_code}")
    print(f"[AuthenticationError] API 키를 확인하세요!")


# ============================================================
# 2부: 재시도 로직 (Exponential Backoff)
# ============================================================
# 일시적 에러(Rate Limit, 서버 오류)는 재시도하면 성공할 수 있습니다.
# 핵심 원칙: 재시도 간격을 점점 늘려서 서버에 부담을 줄이기
#
#   1번째 재시도: 1초 대기
#   2번째 재시도: 2초 대기
#   3번째 재시도: 4초 대기
#   → 대기 시간이 지수적(exponential)으로 증가
print()
print("=" * 60)
print("2부: Exponential Backoff 재시도")
print("=" * 60)


def call_with_retry(messages, max_retries=3, initial_delay=1.0):
    """
    일시적 에러 발생 시 재시도하는 API 호출 함수.

    Args:
        messages: API에 보낼 메시지 리스트
        max_retries: 최대 재시도 횟수
        initial_delay: 첫 번째 재시도 전 대기 시간(초)

    Returns:
        성공 시 응답 텍스트, 실패 시 None
    """
    delay = initial_delay

    for attempt in range(max_retries + 1):  # 최초 1회 + 재시도 횟수
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=256,
                messages=messages,
            )
            return response.content[0].text

        except RateLimitError as e:
            # 429: 요청 제한 초과 → 재시도 가능
            if attempt < max_retries:
                print(f"  [Rate Limit] {delay}초 후 재시도... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2  # 대기 시간 2배로 증가
            else:
                print(f"  [Rate Limit] 최대 재시도 횟수 초과!")
                return None

        except APITimeoutError as e:
            # 타임아웃 → 재시도 가능
            if attempt < max_retries:
                print(f"  [Timeout] {delay}초 후 재시도... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"  [Timeout] 최대 재시도 횟수 초과!")
                return None

        except APIError as e:
            # 500, 529 등 서버 에러 → 재시도 가능
            if e.status_code in (500, 529) and attempt < max_retries:
                print(f"  [서버 에러 {e.status_code}] {delay}초 후 재시도... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                # 재시도 불가능한 에러
                print(f"  [APIError] 상태 코드: {e.status_code}, 메시지: {e.message}")
                return None

        except AuthenticationError:
            # 인증 에러는 재시도해도 소용없음
            print("  [인증 실패] API 키를 확인하세요. 재시도하지 않습니다.")
            return None

        except BadRequestError as e:
            # 잘못된 요청은 재시도해도 소용없음
            print(f"  [잘못된 요청] {e.message}. 재시도하지 않습니다.")
            return None

    return None


# 정상 호출 테스트
print("\n--- 정상 호출 ---")
result = call_with_retry(
    messages=[{"role": "user", "content": "1+1=?"}]
)
print(f"응답: {result}")


# ============================================================
# 3부: Agent 루프에 에러 핸들링 적용
# ============================================================
# Chapter 1-5의 Agent 루프에 에러 처리를 추가한 버전
print()
print("=" * 60)
print("3부: 에러 핸들링이 적용된 Agent 루프")
print("=" * 60)
print("(종료하려면 'quit' 입력)")

conversation_history = []

while True:
    user_input = input("\n사용자: ")
    if user_input.strip().lower() == "quit":
        print("대화를 종료합니다.")
        break

    # 빈 입력 처리
    if not user_input.strip():
        print("  (빈 메시지는 무시됩니다)")
        continue

    conversation_history.append({"role": "user", "content": user_input})

    # 재시도 로직이 포함된 호출
    result = call_with_retry(messages=conversation_history)

    if result is not None:
        # 성공: 응답을 히스토리에 추가
        conversation_history.append({"role": "assistant", "content": result})
        print(f"Claude: {result}")
    else:
        # 실패: 사용자 메시지를 히스토리에서 제거 (실패한 요청은 없던 것으로)
        conversation_history.pop()
        print("  [에러] 응답을 받지 못했습니다. 다시 시도해주세요.")


# ============================================================
# 정리: 에러 핸들링 체크리스트
# ============================================================
print()
print("=" * 60)
print("정리: 에러 핸들링 체크리스트")
print("=" * 60)
print("""
┌─────────────────────┬──────────┬─────────────────────────┐
│ 에러 타입            │ 재시도?  │ 대처법                  │
├─────────────────────┼──────────┼─────────────────────────┤
│ AuthenticationError │ ✗        │ API 키 확인             │
│ BadRequestError     │ ✗        │ 요청 파라미터 수정       │
│ NotFoundError       │ ✗        │ 모델명 등 리소스 확인    │
│ RateLimitError      │ ✓        │ 대기 후 재시도           │
│ APITimeoutError     │ ✓        │ 대기 후 재시도           │
│ APIError (500, 529) │ ✓        │ 대기 후 재시도           │
└─────────────────────┴──────────┴─────────────────────────┘

핵심 원칙:
1. 재시도 가능한 에러와 불가능한 에러를 구분하라
2. Exponential Backoff로 서버 부담을 줄여라
3. 최대 재시도 횟수를 반드시 설정하라 (무한 루프 방지)
4. 실패한 요청은 대화 히스토리에 남기지 마라
""")
