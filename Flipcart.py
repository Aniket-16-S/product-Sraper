# import os
# import time
# import requests
# from playwright.sync_api import sync_playwright

# def get_url() -> str :
#     global Folder
#     q = input("What to search on Flipcart :")
#     Folder = f"Flipcart_{q}"
#     q = q.replace(' ', '+')
#     return f'https://flipkart.com/search?q={q}'

# def scroll(page, delay=0.05, step=500, pause_at_end=2):
#     scroll_height = page.evaluate("() => document.body.scrollHeight")
#     curr_pos = 0
#     while curr_pos < scroll_height:
#         page.evaluate(f"window.scrollTo(0, {curr_pos});")
#         time.sleep(delay)
#         curr_pos += step
#         scroll_height = page.evaluate("() => document.body.scrollHeight")

#     time.sleep(pause_at_end)


from bs4 import BeautifulSoup
from collections.abc import Callable
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
from typing import Callable
from functools import wraps
import time 

def start_chrome() -> None :
    global driver
    options = uc.ChromeOptions()
    options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)
    return

def get_url() -> str :
    global folder
    query = input("Enter what you wanna Search on Flipcart : ").strip()
    folder = query
    query = query.replace(' ', '+' )
    url = f'https://flipkart.com/search?q={query}'
    return url

def safe_eval(func) :
    try :
        return func()
    except Exception :
        return "N/A"


def process_content() :
    driver.get(get_url())
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3.5) 
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_list = soup.find_all('div', attrs={'class':"_1sdMkc LFEi7Z"})
    print(f"found :  {len(product_list)} items")
    for i, product in enumerate(product_list) :
        p_link = safe_eval(lambda : product.find('a', attrs={'class':'rPDeLR'})['href'] )
        img_link = safe_eval( lambda : product.find('img', attrs={"class":"_53J4C-"})['src'] )
        p_company = safe_eval( lambda : product.find('div', attrs={"class":"syl9yP"}).text )
        p_name = safe_eval( lambda : product.find('a', attrs={"class":"WKTcLC"}).get_text() )
        sec = safe_eval( lambda: product.find('a', attrs={"class":"+tlBoD", 'rel':True}) )
        if sec != "N/A" :
            price =safe_eval(lambda: sec.find('div', attrs={'class':"Nx9bqj"}).get_text() )
            o_price = safe_eval(lambda: sec.find('div', attrs={'class':"yRaY8j"}).get_text()  )
            dcount = safe_eval(lambda: sec.find('div', attrs={'class':"UkUFwK"}).get_text()  )
        delv = safe_eval(lambda: product.find('div', attrs={"class":"yiggsN"}).get_text()  )
        if img_link != "N/A" :
            response = requests.get(img_link)
            time.sleep(1.5)
            if response.status_code == 200:
                os.makedirs(f"Flipcart/{folder}", exist_ok=True)
                filename = f"Flipcart/{folder}/product_{i+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(response.content)
                    print(f"\nImage saved as product_{i+1}.jpg")
            else:
                print("\nFailed to download image.")

        print(f"p link : {p_link}\nname : {p_company + " " + p_name}, \nprice :{price} i.e. {o_price} with {dcount} \ndelv : {delv} ")
        print("________________________________________________________________________________________________________________")
    return

        

def main() :
    try :
        start_chrome()
        process_content()
    except Exception as e :
        print(e)
    finally :
        driver.quit()

if __name__ == '__main__' :
    main()