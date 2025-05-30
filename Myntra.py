from playwright.sync_api import sync_playwright
import requests
import os
import time


def get_url() -> str :
    global folder
    query = input("Enter what you wanna Search on Myntra : ").strip()
    folder = query
    query = query.replace(' ', '+' )
    url = f'https://www.myntra.com/{query}?rawQuery={query}'
    return url

def smooth_scroll(page, delay=0.05, step=500, pause_at_end=2):
    scroll_height = page.evaluate("() => document.body.scrollHeight")
    curr_pos = 0
    while curr_pos < scroll_height:
        page.evaluate(f"window.scrollTo(0, {curr_pos});")
        time.sleep(delay)
        curr_pos += step
        scroll_height = page.evaluate("() => document.body.scrollHeight")

    time.sleep(pause_at_end)



with sync_playwright() as p:
    browser = p.webkit.launch(headless=True, args=["--disable-http2"])
    page = browser.new_page(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 800},
    locale="en-US"
    )

    page.goto(get_url())
    page.wait_for_load_state('load')
    page.wait_for_selector("li.product-base")
    smooth_scroll(page, delay=0.05, step=300, pause_at_end=3)
    product_list = page.query_selector_all("li.product-base")


    for i, product in enumerate(product_list):
        
        a_tag = product.query_selector("a[href]")
        p_link = a_tag.get_attribute("href") if a_tag else None

        img_tag = product.query_selector("img[src]")
        img_link = img_tag.get_attribute("src") if img_tag else None

        p_info = product.query_selector("div.product-productMetaInfo")

        title = ""
        if p_info:
            h3 = p_info.query_selector("h3")
            h4 = p_info.query_selector("h4")
            h3_text = h3.text_content().strip() if h3 else ""
            h4_text = h4.text_content().strip() if h4 else ""
            title = f"{h3_text} {h4_text}".strip()
        price_unformatted = ""
        if p_info:
            price_tag = p_info.query_selector("div.product-price")
            price_unformatted = price_tag.text_content().strip() if price_tag else ""

        print(f"Product link : https://myntra.com/{p_link} ", f"img link : {img_link}", f"title : {title}", f"price : {price_unformatted}", sep="\n")
        if img_link:
            try:
                response = requests.get(img_link)
                if response.status_code == 200:
                    os.makedirs(folder, exist_ok=True)
                    filename = f"{folder}/product_{i+1}.jpg"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                        print(f"\nImage saved as product_{i+1}.jpg")
                else:
                    print("\nFailed to download image.")
            except Exception as e:
                print(f"\nError downloading image: {e}")

        print("\n\n\n")
    
    browser.close()