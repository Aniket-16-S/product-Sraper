import asyncio
import aiohttp
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

result = []


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


async def download_image(session, img_url, index):
    if img_url == "N/A":
        return
    try:
        async with session.get(img_url) as response:
            if response.status == 200:
                os.makedirs(f"Flipkart/{folder}", exist_ok=True)
                filename = f"Flipkart/{folder}/product_{index+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(await response.read())
                #print(f"Image saved as product_{index+1}.jpg")
            else:
                pass
                #print(f"Failed to download image {index+1}")
    except Exception as e:
        pass
        #print(f"Error downloading image {index+1}: {e}")


async def process_product(session, product, index):
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

    # print("___START___")
    # print("from Flipkart")
    # print(f"p link : {p_link}")
    # print(f"name : {p_company} {p_name}")
    # print(f"price : {price} i.e. {o_price} with {dcount}")
    # print(f"delv : {delv}")
    # print("___END___")
    
    #                                          Please make sure To Uncomment this if running as __Main__
    
    
    result.append({
        "Product_link": f"p link : {p_link}",
        "Name": f"name : {p_company} {p_name}",
        "Price": f"price : {price} i.e. {o_price} with {dcount}",
        "Delivery": f"delv : {delv}",
    })

    await download_image(session, img_link, index)


async def process_content(Qur=None):
    url = get_url(Qur)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        await page.goto(url)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3.5)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        product_list = soup.find_all('div', {'class': "_1sdMkc LFEi7Z"})
        #print(f"found : {len(product_list)} items")

        async with aiohttp.ClientSession() as session:
            tasks = [process_product(session, product, i) for i, product in enumerate(product_list)]
            await asyncio.gather(*tasks)

        await browser.close()


async def fetch(Qur=None):
    try:
        await process_content(Qur)
    except Exception as e:
        print("from flipkart fetch :", e)
    return json.dumps(result)


if __name__ == '__main__':
    asyncio.run(fetch())
