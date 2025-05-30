import asyncio
import aiohttp
import os
import time
import random
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

driver = None

def start_chrome():
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

def get_url(Qur=None, p_c=None):
    global folder
    if Qur is None:
        query = input("Enter what you wanna Search on Amazon : ").strip()
    else:
        query = Qur
    if p_c is None:
        pc = None
    else:
        pc = p_c
    folder = query
    query = query.replace(' ', '+')
    url = f'https://www.amazon.in/s?k={query}'
    return url, pc

def navigate(url=None, p_c=None, Qur=None):
    if url is None:
        url, p_c = get_url(Qur=Qur, p_c=p_c)
    driver.get(url)
    print("Connecting with Amazon server . . .")
    time.sleep(random.uniform(3, 5))
    if p_c is not None:
        try:
            driver.find_element(By.ID, "nav-global-location-popover-link").click()
            time.sleep(1.5)
            try:
                pincode_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
            except:
                pincode_input = driver.find_element(By.XPATH, "//input[@aria-label='or enter an Indian pincode']")
            pincode_input.clear()
            pincode_input.send_keys(p_c)
            apply_button = driver.find_element(By.ID, "GLUXZipUpdate")
            apply_button.click()
            print("waiting to update . . .")
            time.sleep(5)
        except Exception as e:
            print("Something went wrong while entering pincode ", e)

async def download_image(session, url, folder, i):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                content = await resp.read()
                os.makedirs(f"Amazon/{folder}", exist_ok=True)
                filename = f"Amazon/{folder}/product_{i+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(content)
                print(f"Image saved as product_{i+1}.jpg")
            else:
                print(f"Failed to download image for product {i+1}")
    except Exception as e:
        print(f"Error downloading image for product {i+1}: {e}")

async def process_product(session, product, i, folder):
    try:
        img_url = product.find_element(By.TAG_NAME, 'img').get_attribute('src') or None
        title_section = product.find_element(By.XPATH, ".//div[@data-cy='title-recipe']")
        product_url = title_section.find_element(By.XPATH, ".//a[@class]").get_attribute('href') or None
        product_title = []
        h2s = title_section.find_elements(By.TAG_NAME, 'h2')
        for h2 in h2s:
            product_title.append(h2.text.strip())

        try :
            review_secn = product.find_element(By.XPATH, ".//div[@data-cy='reviews-block']")
            stars = driver.execute_script("return arguments[0].textContent;", review_secn.find_element(By.XPATH, ".//span[@class='a-icon-alt']") ).strip()
            no_of_reviews = driver.execute_script("return arguments[0].textContent;", review_secn.find_element(By.XPATH, ".//span[@aria-hidden='true']") ).strip()
            try :
                sold = driver.execute_script("return arguments[0].textContent;", review_secn.find_element(By.XPATH, ".//span[@class='a-size-base a-color-secondary']") ).strip()
                # Not Available always on page
            except :
                sold = ""
        except Exception as e:
            stars = 'N/A'
            no_of_reviews = ""
            sold = "" 
        try :
            price_secn = product.find_element(By.XPATH, ".//div[@data-cy='price-recipe']") 
            a = price_secn.find_element(By.XPATH, ".//a[@aria-describedby='price-link']")
            cp = driver.execute_script("return arguments[0].textContent;", a.find_element(By.XPATH, ".//span[@class='a-price-whole']")) or None
            mrp = a.find_element(By.XPATH, ".//div[@class='a-section aok-inline-block']").get_attribute('aria-hidden').strip() or None
            discount = driver.execute_script("return arguments[0].textContent;", price_secn.find_element(By.CSS_SELECTOR, "div.a-row > span:last-of-type") ) or None
        except :
            discount = ""
            mrp = ""
            cp = ""   # if price not found,  ... this is when byuing options are not available     
        try :
            delivery_secn = product.find_element(By.XPATH, ".//div[@data-cy='delivery-recipe']")
            final_d = str(driver.execute_script("return arguments[0].textContent;", delivery_secn)).replace('Or', ' Or') or None
        except Exception :
            final_d = ""
        print(f"___START___")
        print("from Amazon :")
        print(f"Name : {''.join(s + ' ' for s in product_title)}")
        print(f"Product link : {product_url}\n")

        if img_url:
            await download_image(session, img_url, folder, i)

        print("___END___")
    except Exception as e:
        print(f"Skipping product {i+1} because {e}")

async def main_process(driver, folder):
    products = driver.find_elements(By.XPATH, "//div[@role='listitem']")
    print(f"Found {len(products)} products")
    async with aiohttp.ClientSession() as session:
        tasks = [process_product(session, product, i, folder) for i, product in enumerate(products)]
        await asyncio.gather(*tasks)

def end():
    try:
        driver.quit()
    except Exception:
        if 'driver' in globals() and driver:
            print("Driver exists but couldn't be deleted somehow . . .")
        else:
            pass
    print("browser closed!")

def fetch(url=None, pc=None, Query=None):
    try:
        start_chrome()
        navigate(url=url, p_c=pc, Qur=Query)
        asyncio.run(main_process(driver, folder))
    except Exception as e:
        print(e)
    finally:
        end()

if __name__ == "__main__":
    fetch()
