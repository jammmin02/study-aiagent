"""
부록 A-5: 비동기 예외 처리

비동기 코드에서 에러가 발생하면 어떻게 될까?
동시에 실행 중인 여러 작업 중 하나가 실패했을 때의 처리 방법을 다룹니다.

4가지 패턴:
    1. 개별 try/except      — 각 코루틴이 자체적으로 에러 처리
    2. gather + return_exceptions — 전부 실행 후 성공/실패 분류
    3. TaskGroup            — 하나 실패 시 나머지 자동 취소
    4. 재시도 (Retry)       — 일시적 오류에 N회 재시도
"""

import asyncio


# ── 공통: API 호출 시뮬레이션 ────────────────────

async def call_api(name: str, fail: bool = False) -> str:
    await asyncio.sleep(1)
    if fail:
        raise ConnectionError(f"{name} 서버 연결 실패")
    return f"{name} 응답 OK"


# ============================================================
# 패턴 1: 개별 try/except
# ============================================================
# 각 작업이 독립적이고, 하나가 실패해도 나머지는 계속 진행할 때

async def safe_call(name: str) -> str:
    try:
        return await call_api(name, fail=(name == "결제"))
    except ConnectionError as e:
        print(f"  [에러] {e}")
        return f"{name} 실패 — 기본값 반환"


async def pattern1():
    print("[패턴 1] 개별 try/except")
    results = await asyncio.gather(
        safe_call("인증"),
        safe_call("결제"),     # 실패해도 다른 작업 정상 진행
        safe_call("알림"),
    )
    for r in results:
        print(f"  결과: {r}")


# ============================================================
# 패턴 2: gather + return_exceptions
# ============================================================
# 모든 작업을 실행한 뒤, 성공과 실패를 한꺼번에 분류할 때
#
# return_exceptions=False (기본값):
#   → 하나라도 실패하면 gather 자체가 예외를 던짐
#
# return_exceptions=True:
#   → 예외 객체를 결과 리스트에 포함, gather는 중단되지 않음

async def pattern2():
    print("\n[패턴 2] gather + return_exceptions=True")
    results = await asyncio.gather(
        call_api("인증"),
        call_api("결제", fail=True),
        call_api("알림"),
        return_exceptions=True,         # 예외도 결과로 취급
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"  [실패] {r}")
        else:
            print(f"  [성공] {r}")


# ============================================================
# 패턴 3: TaskGroup — 하나 실패 시 전체 취소 (Python 3.11+)
# ============================================================
# 전부 성공해야 의미 있는 작업 (예: 트랜잭션)

async def pattern3():
    print("\n[패턴 3] TaskGroup — 하나 실패 → 전체 취소")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(call_api("인증"))
            tg.create_task(call_api("결제", fail=True))  # 실패 → 나머지 취소
            tg.create_task(call_api("알림"))
    except* ConnectionError as eg:
        for e in eg.exceptions:
            print(f"  [취소됨] {e}")


# ============================================================
# 패턴 4: 재시도 (Retry)
# ============================================================
# 네트워크 오류 등 일시적 실패에 대해 N회 재시도

async def call_with_retry(name: str, max_retries: int = 3) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            fail = (attempt < 3)  # 시뮬레이션: 3번째에 성공
            result = await call_api(name, fail=fail)
            print(f"  {name}: {attempt}번째 시도 성공")
            return result
        except ConnectionError:
            print(f"  {name}: {attempt}번째 시도 실패")
            if attempt == max_retries:
                raise
            await asyncio.sleep(0.5)  # 재시도 전 대기


async def pattern4():
    print("\n[패턴 4] 재시도 (Retry)")
    result = await call_with_retry("결제")
    print(f"  최종 결과: {result}")


# ============================================================
# 실행
# ============================================================

async def main():
    await pattern1()
    await pattern2()
    await pattern3()
    await pattern4()

    print()
    print("=" * 50)
    print("[정리]")
    print("  패턴 1: 개별 try/except    → 실패해도 다른 작업 계속")
    print("  패턴 2: return_exceptions  → 전부 실행 후 성공/실패 분류")
    print("  패턴 3: TaskGroup          → 하나 실패 시 전체 취소")
    print("  패턴 4: Retry              → 일시적 오류에 재시도")


if __name__ == "__main__":
    asyncio.run(main())
