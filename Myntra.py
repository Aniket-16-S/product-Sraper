import os
import asyncio
from playwright.async_api import async_playwright
import aiohttp

queue = None  
folder = None
url_name = {}

def get_url(Query) -> str:
    global folder
    if Query is None:
        query = input("Enter what you wanna Search on Myntra : ").strip()
    else:
        query = Query
    folder = query
    query = query.replace(' ', '+')
    return f'https://www.myntra.com/{query}?rawQuery={query}'


async def smooth_scroll(page, delay=0.05, step=500, pause_at_end=2):
    scroll_height = await page.evaluate("() => document.body.scrollHeight")
    curr_pos = 0
    while curr_pos < scroll_height:
        await page.evaluate(f"window.scrollTo(0, {curr_pos});")
        await asyncio.sleep(delay)
        curr_pos += step
        scroll_height = await page.evaluate("() => document.body.scrollHeight")
    await asyncio.sleep(pause_at_end)


async def download_image(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                os.makedirs(f"Myntra/{folder}", exist_ok=True)
                name = url_name[url]
                filename = f"Myntra/{folder}/{name}"
                with open(filename, "wb") as f:
                    f.write(await response.read())
    except Exception:
        pass


async def process_product(i, product, session):
    try:
        a_tag = await product.query_selector("a[href]")
        p_link = await a_tag.get_attribute("href") if a_tag else None

        img_tag = await product.query_selector("img[src]")
        img_link = await img_tag.get_attribute("src") if img_tag else None

        p_info = await product.query_selector("div.product-productMetaInfo")

        title = ""
        if p_info:
            h3 = await p_info.query_selector("h3")
            h4 = await p_info.query_selector("h4")
            h3_text = (await h3.text_content()).strip() if h3 else ""
            h4_text = (await h4.text_content()).strip() if h4 else ""
            title = f"{h3_text} {h4_text}".strip()

        price_unformatted = ""
        if p_info:
            price_tag = await p_info.query_selector("div.product-price")
            price_unformatted = (await price_tag.text_content()).strip() if price_tag else ""

        info = {
            "Name": f"title : {title}",
            "product_link": f"https://myntra.com/{p_link}",
            "review" : None,
            "price": f"price : {price_unformatted}",
            "delivery" : None,
            "index" : i
        }

        if img_link:
            url_name[img_link] = f"product_{i}.jpg"
            await download_image(session, img_link)

        await queue.put(info)

    except Exception:
        pass


async def process_content(url=None, Query=None, context=None):
    if url is None:
        url = get_url(Query)

    if not context:
        p = await async_playwright().start()
        browser = await p.webkit.launch(headless=True, args=["--disable-http2"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )

    page = await context.new_page()
    await page.goto(url)
    await page.wait_for_load_state('load')
    await page.wait_for_selector("li.product-base")
    await smooth_scroll(page, delay=0.05, step=300, pause_at_end=3)
    product_list = await page.query_selector_all("li.product-base")

    async with aiohttp.ClientSession() as session:
        tasks = [process_product(i, product, session) for i, product in enumerate(product_list)]
        await asyncio.gather(*tasks)

    await queue.put(None)


async def fetch(Query=None, context=None):
    global queue
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(process_content(Query=Query, context=context))
    while True:
        item = await queue.get()
        if item is None:
            break
        yield item
    await producer_task


if __name__ == "__main__":
    async def main():
        async for item in fetch("shoes"):
            print(item)

    asyncio.run(main())
