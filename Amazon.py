import asyncio
import aiohttp
import os
import time
import random
from playwright.async_api import async_playwright
import json

result = []

async def get_url(Qur=None, p_c=None):
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
    return url, pc, folder

async def download_image(session, url, folder, i):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                content = await resp.read()
                os.makedirs(f"Amazon/{folder}", exist_ok=True)
                filename = f"Amazon/{folder}/product_{i+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(content)
                #print(f"Image saved as product_{i+1}.jpg")
            else:
                pass
                #print(f"Failed to download image for product {i+1}")
    except Exception as e:
        pass
        
        #print(f"Error downloading image for product {i+1}: {e}")

async def process_product(session, product, i, folder):
    try:
        img = await product.query_selector("img")
        img_url = await img.get_attribute('src') if img else None

        title_section = await product.query_selector("[data-cy='title-recipe']")
        title_links = await title_section.query_selector_all("h2") if title_section else []
        product_title = [await h2.inner_text() for h2 in title_links]
        a_tag = await title_section.query_selector("a") if title_section else None
        product_url = await a_tag.get_attribute('href') if a_tag else None

        try:
            review_secn = await product.query_selector("[data-cy='reviews-block']")
            stars = (await (await review_secn.query_selector(".a-icon-alt")).inner_text()).strip()
            no_of_reviews = (await (await review_secn.query_selector("[aria-hidden='true']")).inner_text()).strip()
            try:
                sold = (await (await review_secn.query_selector(".a-size-base.a-color-secondary")).inner_text()).strip()
            except:
                sold = ""
        except:
            stars = 'N/A'
            no_of_reviews = ""
            sold = ""

        try:
            price_secn = await product.query_selector("[data-cy='price-recipe']")
            a = await price_secn.query_selector("[aria-describedby='price-link']")
            cp = (await (await a.query_selector(".a-price-whole")).inner_text()).strip()
            mrp = await a.get_attribute("aria-hidden")
            discount_el = await price_secn.query_selector("div.a-row > span:last-of-type")
            discount = (await discount_el.inner_text()).strip() if discount_el else ""
        except:
            cp = mrp = discount = ""

        try:
            delivery_secn = await product.query_selector("[data-cy='delivery-recipe']")
            final_d = (await delivery_secn.inner_text()).replace('Or', ' Or') if delivery_secn else ""
        except:
            final_d = ""

        name = ' '.join(product_title)
        # print(f"___START___")
        # print("from Amazon :")
        # print(f"Name : {name}")
        # print(f"Product link : {product_url}\n")
        # print(f"stars:{stars}, no of rev : {no_of_reviews} , {sold} sold in past month")
        # print(f"Price : {cp} ( {mrp} with {discount} off)")
        # print(f"Delivery : {final_d}")
        # print(f"___END___")

        result.append({
            "Name": name,
            "product_link": f"https://www.amazon.in{product_url}" if product_url else None,
            "rev": f"stars:{stars}, no of rev : {no_of_reviews} , {sold} sold in past month",
            "price": f"Price : {cp} ( {mrp} with {discount} off)",
            "delivery": f"Delivery : {final_d}"
        })

        if img_url:
            await download_image(session, img_url, folder, i)

    except Exception as e:
        pass
        
        #print(f"Skipping product {i+1} because {e}")

async def process_content(Qur=None, p_c=None):
    url, pc, folder = await get_url(Qur=Qur, p_c=p_c)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")
        page = await context.new_page()

        #print("Connecting with Amazon server . . .")
        await page.goto(url)
        await page.wait_for_timeout(random.uniform(3000, 5000))

        # Handle pincode
        if pc:
            try:
                await page.click("#nav-global-location-popover-link")
                await page.wait_for_timeout(1500)
                try:
                    pincode_input = await page.query_selector("#GLUXZipUpdateInput")
                except:
                    pincode_input = await page.query_selector("//input[@aria-label='or enter an Indian pincode']")
                await pincode_input.fill(pc)
                await page.click("#GLUXZipUpdate")
                print("waiting to update . . .")
                await page.wait_for_timeout(5000)
            except Exception as e:
                print("Something went wrong while entering pincode ", e)

        # Scraping part
        products = await page.query_selector_all("div[role='listitem']")
        #print(f"Found {len(products)} products")

        async with aiohttp.ClientSession() as session:
            tasks = [process_product(session, product, i, folder) for i, product in enumerate(products)]
            await asyncio.gather(*tasks)

        await browser.close()

    return result

async def fetch(Qur = None) :
    try :
        await process_content(Qur)
    except Exception as e :
        print("from amazon fetch :", e)
    return json.dumps(result)


if __name__ == "__main__":
    asyncio.run(fetch())
