"""
부록 A-3: Task와 Future — 동시 실행의 핵심

await만으로는 "순차 실행"밖에 안 됩니다.
동시에 여러 작업을 돌리려면 코루틴을 Task로 만들어
이벤트 루프의 대기열에 등록해야 합니다.

핵심 개념:
    - Future: 아직 결과가 없지만, 나중에 결과가 채워질 "빈 상자"
    - Task:   Future + 코루틴을 실행하는 기능 (Future의 하위 클래스)
    - create_task(): 코루틴 → Task로 감싸서 이벤트 루프에 등록

    1 Task = 1 코루틴 (항상 1:1 관계)
"""

import asyncio


async def make_coffee(menu: str) -> str:
    print(f"  {menu} 제조 시작")
    await asyncio.sleep(2)
    print(f"  {menu} 제조 완료")
    return menu


# ============================================================
# 1. await만 사용 — 순차 실행 (약 6초)
# ============================================================

async def sequential():
    print("[1] await만 사용 — 순차 실행")

    r1 = await make_coffee("아메리카노")  # 2초 대기
    r2 = await make_coffee("라떼")        # 2초 대기
    r3 = await make_coffee("카푸치노")    # 2초 대기

    print(f"  결과: {r1}, {r2}, {r3}\n")


# ============================================================
# 2. create_task — 동시 실행 (약 2초)
# ============================================================

async def concurrent():
    """
    create_task()로 코루틴을 Task로 만들면:
      1. 이벤트 루프 대기열에 등록됨 (바로 다음 줄 실행)
      2. 현재 코루틴이 await로 양보할 때 Task가 실행됨
      3. await task로 결과를 받을 수 있음
    """
    print("[2] create_task — 동시 실행")

    # 3개를 동시에 이벤트 루프에 등록
    task1 = asyncio.create_task(make_coffee("아메리카노"))
    task2 = asyncio.create_task(make_coffee("라떼"))
    task3 = asyncio.create_task(make_coffee("카푸치노"))
    # 이 시점에서 3개 Task가 대기열에 들어감 (아직 실행 X)

    # await로 양보하면 루프가 대기열의 Task들을 실행
    r1 = await task1
    r2 = await task2
    r3 = await task3

    print(f"  결과: {r1}, {r2}, {r3}\n")


# ============================================================
# 3. Task 상태 확인 — done(), result()
# ============================================================

async def task_status():
    """Task는 Future를 상속하므로 상태와 결과를 확인할 수 있습니다."""
    print("[3] Task 상태 확인")

    task = asyncio.create_task(make_coffee("아메리카노"))

    print(f"  완료 여부: {task.done()}")     # False — 아직 실행 안 됨

    await task                                # 완료 대기

    print(f"  완료 여부: {task.done()}")     # True
    print(f"  결과값:   {task.result()}")    # "아메리카노"
    print()


# ============================================================
# 4. 주의: create_task만 하고 await 안 하면?
# ============================================================

async def no_await():
    """
    await 없이 create_task만 하면:
    현재 함수가 바로 끝남 → 이벤트 루프 종료 → Task 실행 안 됨
    """
    print("[4] create_task만 하고 await 안 하면?")

    asyncio.create_task(make_coffee("아메리카노"))
    asyncio.create_task(make_coffee("라떼"))
    # ← 여기서 함수 종료 → 루프가 닫히면 Task들은 실행 기회 없이 소멸
    print("  → 함수가 바로 종료됨 (Task들은 실행되지 않음)\n")


# ============================================================
# 실행
# ============================================================

async def main():
    import time

    print("=" * 50)
    start = time.time()
    await sequential()
    print(f"  소요시간: {time.time() - start:.1f}초")

    print("=" * 50)
    start = time.time()
    await concurrent()
    print(f"  소요시간: {time.time() - start:.1f}초")

    print("=" * 50)
    await task_status()

    print("=" * 50)
    await no_await()

    print("=" * 50)
    print("[정리]")
    print("  await func()        → 끝날 때까지 멈춤 (순차)")
    print("  create_task(func()) → 루프에 등록, 바로 다음 줄 (동시)")
    print("  await task          → Task 완료 대기 + 결과 수신")
    print("  task.done()         → 완료 여부 확인")
    print("  task.result()       → 완료 후 결과값 가져오기")


if __name__ == "__main__":
    asyncio.run(main())
