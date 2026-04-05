"""
부록 A-4: 자주 쓰는 비동기 패턴

실무에서 가장 많이 사용하는 비동기 패턴 3가지를 다룹니다:

    1. gather  — 여러 작업을 동시에 실행하고 모든 결과를 받기
    2. TaskGroup — 구조적 동시성 (Python 3.11+, 에러 처리 강화)
    3. async for / async with — 비동기 반복과 컨텍스트 매니저
"""

import asyncio


# ============================================================
# 준비: API 호출 시뮬레이션
# ============================================================

async def call_api(name: str, delay: float) -> dict:
    """외부 API 호출 시뮬레이션"""
    print(f"  📡 {name} API 호출 중...")
    await asyncio.sleep(delay)
    return {"api": name, "status": "ok", "delay": delay}


# ============================================================
# 패턴 1: asyncio.gather — 동시 실행 후 결과 모으기
# ============================================================

async def pattern_gather():
    """
    gather: 여러 비동기 작업을 동시에 실행하고, 모든 결과를 리스트로 반환
    → 서로 독립적인 API 여러 개를 동시에 호출할 때 사용
    """
    print("[패턴 1] asyncio.gather")
    print()

    results = await asyncio.gather(
        call_api("날씨", 1.0),
        call_api("뉴스", 1.5),
        call_api("주식", 0.5),
    )

    # 결과는 호출 순서대로 반환됨 (완료 순서가 아님!)
    for r in results:
        print(f"  결과: {r}")
    print()


# ============================================================
# 패턴 2: TaskGroup — 구조적 동시성 (Python 3.11+)
# ============================================================

async def pattern_taskgroup():
    """
    TaskGroup: gather와 비슷하지만, 하나가 실패하면 나머지를 자동 취소
    → 모든 작업이 성공해야 의미 있는 경우에 적합
    """
    print("[패턴 2] TaskGroup (Python 3.11+)")
    print()

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(call_api("인증", 0.5))
        task2 = tg.create_task(call_api("프로필", 1.0))
        task3 = tg.create_task(call_api("설정", 0.8))

    # TaskGroup 블록을 나오면 모든 task가 완료된 상태
    print(f"  결과1: {task1.result()}")
    print(f"  결과2: {task2.result()}")
    print(f"  결과3: {task3.result()}")
    print()


# ============================================================
# 패턴 3: async with — 비동기 컨텍스트 매니저
# ============================================================
# MCP 클라이언트 등에서 자주 사용하는 패턴입니다.

class AsyncConnection:
    """비동기 연결 시뮬레이션 (MCP 서버 연결과 유사)"""

    def __init__(self, server: str):
        self.server = server

    async def __aenter__(self):
        """연결 시작 (async with 진입 시)"""
        print(f"  🔌 {self.server} 연결 중...")
        await asyncio.sleep(0.5)
        print(f"  ✅ {self.server} 연결 완료")
        return self

    async def __aexit__(self, *args):
        """연결 종료 (async with 탈출 시 — 에러가 나도 반드시 실행)"""
        print(f"  🔌 {self.server} 연결 해제")

    async def query(self, q: str) -> str:
        await asyncio.sleep(0.3)
        return f"[{self.server}] '{q}' 결과"


async def pattern_async_with():
    """
    async with: 리소스 연결/해제를 자동으로 관리
    → DB 연결, MCP 서버 세션, 파일 핸들 등에 사용
    """
    print("[패턴 3] async with (비동기 컨텍스트 매니저)")
    print()

    # with 블록을 나가면 자동으로 연결이 해제됨 (에러가 나도!)
    async with AsyncConnection("MCP서버") as conn:
        result = await conn.query("도구 목록")
        print(f"  결과: {result}")
    print()


# ============================================================
# 실행
# ============================================================

async def main():
    print("=" * 50)
    await pattern_gather()

    print("=" * 50)
    await pattern_taskgroup()

    print("=" * 50)
    await pattern_async_with()

    print("=" * 50)
    print("[정리]")
    print("  gather     → 여러 작업 동시 실행, 결과 리스트 반환")
    print("  TaskGroup  → gather + 하나 실패 시 전체 취소 (안전)")
    print("  async with → 리소스 연결/해제 자동 관리")


if __name__ == "__main__":
    asyncio.run(main())
