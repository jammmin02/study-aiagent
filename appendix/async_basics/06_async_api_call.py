"""
부록 A-6: 비동기 실전 — Claude API 비동기 호출

이 수업에서 비동기가 실제로 필요한 대표적인 상황:

    1. MCP 클라이언트가 서버와 통신할 때 (네트워크 I/O)
    2. 여러 LLM 호출을 동시에 보낼 때 (병렬 API 호출)
    3. 웹 서버(Flask/FastAPI)에서 요청을 처리할 때

이 예제에서는 Anthropic의 AsyncAnthropic 클라이언트로
Claude API를 비동기로 호출하는 방법을 보여줍니다.
"""

import time
import asyncio
from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"  # 빠른 응답을 위해 Haiku 사용


# ============================================================
# 1. 동기 방식: 3개 질문을 순차적으로 호출
# ============================================================

def run_sync():
    """동기 클라이언트로 3개 질문을 하나씩 호출"""
    client = Anthropic()
    questions = [
        "Python을 한 문장으로 설명해줘",
        "JavaScript를 한 문장으로 설명해줘",
        "Rust를 한 문장으로 설명해줘",
    ]

    print("[동기 방식] 3개 질문 순차 호출")
    start = time.time()

    for q in questions:
        response = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": q}],
        )
        print(f"  Q: {q}")
        print(f"  A: {response.content[0].text[:50]}...")
        print()

    elapsed = time.time() - start
    print(f"→ 총 소요시간: {elapsed:.1f}초\n")


# ============================================================
# 2. 비동기 방식: 3개 질문을 동시에 호출
# ============================================================

async def ask(client: AsyncAnthropic, question: str) -> str:
    """비동기로 하나의 질문을 보내고 답변을 받는 함수"""
    response = await client.messages.create(   # ← await로 비동기 호출
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


async def run_async():
    """비동기 클라이언트로 3개 질문을 동시에 호출"""
    client = AsyncAnthropic()  # ← 비동기 전용 클라이언트
    questions = [
        "Python을 한 문장으로 설명해줘",
        "JavaScript를 한 문장으로 설명해줘",
        "Rust를 한 문장으로 설명해줘",
    ]

    print("[비동기 방식] 3개 질문 동시 호출")
    start = time.time()

    # 3개 질문을 동시에 전송
    answers = await asyncio.gather(
        ask(client, questions[0]),
        ask(client, questions[1]),
        ask(client, questions[2]),
    )

    for q, a in zip(questions, answers):
        print(f"  Q: {q}")
        print(f"  A: {a[:50]}...")
        print()

    elapsed = time.time() - start
    print(f"→ 총 소요시간: {elapsed:.1f}초")
    print("  (동기 대비 약 1/3 — 3개 요청이 동시에 처리되므로)\n")


# ============================================================
# 실행 비교
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    run_sync()

    print("=" * 60)
    asyncio.run(run_async())

    print("=" * 60)
    print("[핵심 차이점]")
    print("  동기:  Anthropic()         + client.messages.create()")
    print("  비동기: AsyncAnthropic()    + await client.messages.create()")
    print()
    print("[언제 비동기를 쓸까?]")
    print("  - 여러 API를 동시에 호출할 때 (이 예제)")
    print("  - MCP 서버/클라이언트 통신 (chapter4)")
    print("  - 웹 서버에서 여러 요청을 동시 처리할 때")
