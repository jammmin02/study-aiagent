import asyncio
import time

async def make_coffee(item:str) -> None:
   print(f"{menu} 준비 중")
   
   # asyncio.sleep(2)
   time.sleep(2)
   
   print(f"{menu} 준비 완료")
   
async def main()-> None:
   start_time = time.time()
   make_coffee("라떼")
   make_coffee("아메리카노")
   make_coffee("말차")
   
   elapsed = time.time() - start_time
   print(f"총 소요시간: {elapsed:.1f}")
   
if __name__ == "__main__":
   asyncio.run(main())