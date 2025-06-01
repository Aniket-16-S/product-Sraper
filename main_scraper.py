import asyncio, time
import Myntra as m
import Amazon as a
import Flipcart as f
from playwright.async_api import async_playwright

async def collect_to_queue(source_name, gen, queue):
    async for item in gen:
        if item:
            await queue.put((source_name, item))
    # Signals that this source is done
    await queue.put((source_name, None))

async def merged_printer(sources, lock):
    queue = asyncio.Queue()
    total_done = 0
    total_sources = len(sources)
    product_count = 0

    # Launches all collectors
    tasks = [asyncio.create_task(collect_to_queue(name, gen, queue)) for name, gen in sources]

    while total_done < total_sources:
        source, item = await queue.get()
        if item is None:
            total_done += 1
            continue

        product_count += 1
        async with lock:
            print(f"\n===== Product {product_count} -- {source} =====")
            for k, v in item.items():
                print(f"{k} : {v}")
            print("\n")

    await asyncio.gather(*tasks)
    return product_count

async def main():
    async with async_playwright() as p:
        lock = asyncio.Lock()

        # Browser for Amazon & Flipkart
        chrom_browser  = await p.chromium.launch(headless=True)
        chrom_context  = await chrom_browser.new_context()
        # Webkit B for Myntra. Experimental !
        webkit_browser = await p.webkit.launch(headless=True, args=["--disable-http2"])
        webkit_context = await webkit_browser.new_context()

        query = input("Search for : ").strip()
        t0 = time.time()

        # Sources as (name, generator)
        sources = [
            ("Myntra", m.fetch(Query=query, context=webkit_context)),
            ("Amazon", a.fetch(Query=query, context=chrom_context)),
            ("Flipkart", f.fetch(Query=query, context=chrom_context)),
        ]

        total = await merged_printer(sources, lock)
        dt = time.time() - t0

        print(f"\n🕒 Done in {dt:.4f}s — Total products scraped: {total}")

if __name__ == "__main__":
    asyncio.run(main())
