import asyncio
import aiohttp
import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

driver = None
folder = None

def start_chrome():
    global driver
    options = uc.ChromeOptions()
    options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'  # Set yours
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)

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
                print(f"Image saved as product_{index+1}.jpg")
            else:
                print(f"Failed to download image {index+1}")
    except Exception as e:
        print(f"Error downloading image {index+1}: {e}")

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

    print("___START___")
    print("from Flipkart")
    print(f"p link : {p_link}")
    print(f"name : {p_company} {p_name}")
    print(f"price : {price} i.e. {o_price} with {dcount}")
    print(f"delv : {delv}")
    print("___END___")

    await download_image(session, img_link, index)

async def process_content(Qur=None):
    url = get_url(Qur)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_list = soup.find_all('div', {'class': "_1sdMkc LFEi7Z"})
    print(f"found : {len(product_list)} items")

    async with aiohttp.ClientSession() as session:
        tasks = [process_product(session, product, i) for i, product in enumerate(product_list)]
        await asyncio.gather(*tasks)

def fetch(Qur=None):
    try:
        start_chrome()
        asyncio.run(process_content(Qur))
    except Exception as e:
        print(e)
    finally:
        if 'driver' in globals() and driver:
            driver.quit()
        else:
            pass

if __name__ == '__main__':
    fetch()
