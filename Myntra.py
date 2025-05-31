import os
import asyncio
from playwright.async_api import async_playwright
import aiohttp
import json

folder = None
result = []

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

async def download_image(session, url, i):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                os.makedirs(f"Myntra/{folder}", exist_ok=True)
                filename = f"Myntra/{folder}/product_{i+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(await response.read())
                #print(f"Image saved as product_{i+1}.jpg")
            else:
                pass
                #print(f"Failed to download image {i+1}")
    except Exception as e:
        #print(f"Error downloading image {i+1}: {e}")
        pass

async def process_product(i, product, session):
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

    # print("___START___")
    # print("from Myntra")
    # print(f"Product link : https://myntra.com/{p_link}")
    # print(f"img link : {img_link}")
    # print(f"title : {title}")
    # print(f"price : {price_unformatted}")
    # print("___END___")

    #                                          Please make sure To Uncomment this if running as __Main__
    
    result.append({
        "Name" : f"title : {title}",
        "Product-link" : f"Product link : https://myntra.com/{p_link}" ,
        "Price" : f"price : {price_unformatted}"
    })

    if img_link:
        await download_image(session, img_link, i)

async def fetch(url=None, Query=None):
    if url is None:
        url = get_url(Query)

    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=True, args=["--disable-http2"])
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        await page.goto(url)
        await page.wait_for_load_state('load')
        await page.wait_for_selector("li.product-base")
        await smooth_scroll(page, delay=0.05, step=300, pause_at_end=3)
        product_list = await page.query_selector_all("li.product-base")

        tasks = []

        async with aiohttp.ClientSession() as session:
            for i, product in enumerate(product_list):  
                tasks.append(process_product(i, product, session))

            await asyncio.gather(*tasks)

        await browser.close()
        #print(*result)
        return json.dumps(result)

if __name__ == "__main__":
    asyncio.run(fetch())
