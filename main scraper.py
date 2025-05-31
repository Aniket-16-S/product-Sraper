import asyncio
import Myntra as m
import Amazon as a
import Flipcart as f
import time
import json

perfo = None
lens:int = 0

async def main():
    q = input("Enter what to search: ")
    queries = q

    start = time.time()

    tasks = [m.fetch(Query=queries), a.fetch(Qur=queries), f.fetch(Qur=queries)]
    mnt, amz, flipk = await asyncio.gather(*tasks)

    end = time.time()
    
    global perfo
    global lens
    perfo = end - start
    
    mnt = json.loads(mnt)
    amz = json.loads(amz)
    flipk = json.loads(flipk)
    for take in [mnt, amz, flipk] :
        for prod in take :
            print(f'\n{prod}\n\n')
            lens += 1

    print("Time : ", perfo, "Comparisons : ", lens-6) # around 6 products are blank from amazon. No idea why . . .

if __name__ == '__main__':
    asyncio.run(main())
