import asyncio
import aiohttp
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

queue = None  
folder = None
url_name = {}

def get_url(Qur=None):
    global folder
    if Qur is None:
        query = input("Enter what you wanna Search on Flipkart: ").strip()
    else:
        query = Qur
    folder = query
    query = query.replace(' ', '+')
    return f'https://www.flipkart.com/search?q={query}'

def safe_eval(func):
    try:
        return func()
    except Exception:
        return "N/A"

async def download_image(session, img_url):
    if img_url == "N/A":
        return
    try:
        async with session.get(img_url) as response:
            if response.status == 200:
                os.makedirs(f"Flipkart/{folder}", exist_ok=True)
                name = url_name[img_url]
                filename = f"Flipkart/{folder}/{name}"
                with open(filename, "wb") as f:
                    f.write(await response.read())
    except Exception:
        pass

async def process_product(session, product, index):
    try:
        p_link = safe_eval(lambda: product.find('a', {'class': 'rPDeLR'})['href'])
        img_link = safe_eval(lambda: product.find('img', {'class': '_53J4C-'})['src'])
        p_company = safe_eval(lambda: product.find('div', {'class': 'syl9yP'}).text)
        p_name = safe_eval(lambda: product.find('a', {'class': 'WKTcLC'}).get_text())
        sec = safe_eval(lambda: product.find('a', {'class': '+tlBoD', 'rel': True}))

        price = o_price = dcount = "N/A"
        if sec != "N/A":
            price = safe_eval(lambda: sec.find('div', {'class': 'Nx9bqj'}).get_text())
            o_price = safe_eval(lambda: sec.find('div', {'class': 'yRaY8j'}).get_text())
            dcount = safe_eval(lambda: sec.find('div', {'class': 'UkUFwK'}).get_text())

        delv = safe_eval(lambda: product.find('div', {'class': 'yiggsN'}).get_text())

        info = {
            "Name": f"{p_company} {p_name}",
            "product_link": f"https://www.flipkart.com/{p_link}",
            "review" : None,
            "price": f"{price} ( {o_price} with {dcount})",
            "delivery": f"{delv}",
            "index" : index
        }
        if img_link :
            url_name[img_link] = f"product_{index}.jpg"
            await download_image(session, img_link)
        await queue.put(info)

    except Exception:
        pass

async def process_content(Qur=None, context=None):
    url = get_url(Qur)
    if not context:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            viewport={"width": 1920, "height": 1080}
        )
    page = await context.new_page()
    await page.goto(url)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(5)
    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')
    product_list = soup.find_all('div', {'class': "_1sdMkc LFEi7Z"})
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_product(session, product, i) for i, product in enumerate(product_list)]
        await asyncio.gather(*tasks)

    await queue.put(None)

async def fetch(Query=None, context=None):
    global queue
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(process_content(Qur=Query, context=context))
    while True:
        item = await queue.get()
        if item is None:
            break
        yield item
    await producer_task

if __name__ == '__main__':
    async def main():
        async for item in fetch("iphone"):
            print(item)

    asyncio.run(main())
