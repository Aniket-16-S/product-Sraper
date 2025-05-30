from collections.abc import Callable
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random
import requests
import os

def start_chrome() -> None :
    global driver
    options = uc.ChromeOptions()
    options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe' 
    # Please make sure to add your own path for browser.
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
    query = input("Enter what you wanna Search on Amazon : ").strip()
    folder = query
    query = query.replace(' ', '+' )
    url = f'https://www.amazon.in/s?k={query}'
    return url

def get_pincode() -> int :
    pincode = input("Enter your pincode to get relevent delivery info (else hit enter) :")
    try :
        pincode = int(pincode)
        if not len(str(pincode)) == 6 : 
            print("Pincode incorrect")
            return None
        return pincode
    except ValueError :
            if pincode == "" :
               print("skipping pincode custmisation. DELIVRY INFO. MAY NOT BE RELEVENT FOR YOU !")
            else :
               print("Pincode Ignored becase probably you entered character")
            return None
    except Exception as e:
        print(e)
        return None 
 
def navigate() -> None :
    url = get_url()
    driver.get(url)
    print("Connecting with Amazon server . . .")
    time.sleep(random.uniform(3, 5))
    p_c = get_pincode()
    if p_c is not None :
        try :
            driver.find_element(By.ID, "nav-global-location-popover-link").click()
            time.sleep(1.5) # Necessary ! Do NOT remove
            try :
                pincode_input = driver.find_element(By.ID, "GLUXZipUpdateInput") # Never gets error but just in case.
            except :
                pincode_input = driver.find_element(By.XPATH, "//input[@aria-label='or enter an Indian pincode']")
            pincode_input.clear()
            pincode_input.send_keys(p_c)
            apply_button = driver.find_element(By.ID, "GLUXZipUpdate")
            apply_button.click()
            print("waiting to update . . .")
            time.sleep(5) # Page content gets refreshed with new info. so ...       
        except Exception as e :
            print("Something went wrong while entering pincode ", e)
    return

def process_content() :
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4)) # For Lazy Loads
    items = driver.find_elements(By.XPATH, "//div[@role='listitem']")
    print("Found : ",len(items), " items")
    for i, product in enumerate(items) :
        try :
            img_url = product.find_element(By.TAG_NAME, 'img').get_attribute('src') or None
            title_section = product.find_element(By.XPATH, ".//div[@data-cy='title-recipe']")
            product_url = title_section.find_element(By.XPATH, ".//a[@class]").get_attribute('href') or None
            product_title = []
            h2s = title_section.find_elements(By.TAG_NAME, 'h2') # prdct MfG company and prdct title both are in <h2> tag so . . .
            for h2 in h2s:
                product_title.append(driver.execute_script("return arguments[0].textContent;", h2 ).strip())
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
                continue   # if price not found, skip to next prdct ... this is when byuing options are not available     
            delivery_secn = product.find_element(By.XPATH, ".//div[@data-cy='delivery-recipe']")
            final_d = str(driver.execute_script("return arguments[0].textContent;", delivery_secn)).replace('Or', ' Or') or None
            print(f"\n\n--------------------  Product {i+1}  --------------------------")
            print(f"Name : ", ''.join(s + " " for s in product_title ))
            print(f"ratings : {stars}   {no_of_reviews}-reviews , {sold}")
            print(f"Price : ₹{cp}  |  {mrp} with {discount}")
            print(f"Delivery : {final_d}")
            print(f"\n\nProduct link : {product_url}\n")
            response = requests.get(img_url)
            time.sleep(1.5)
            if response.status_code == 200:
                os.makedirs(f"{folder}", exist_ok=True)
                filename = f"{folder}/product_{i+1}.jpg"
                with open(filename, "wb") as f:
                    f.write(response.content)
                    print(f"\nImage saved as product_{i+1}.jpg")
            else:
                print("\nFailed to download image.")
        except Exception as e:
            print(f"Skiping prdct {i+1} because ", next((s for s in [e[:91]]))) # genrator -> first 90 chars of exception ...
            continue
    print("Complete")
    return

def end() :
    driver.quit()
    print("browser closed !")

def main() :
    try :
        start_chrome()
        navigate()
        process_content()
    except Exception as e :
        print(e)
    finally :
        end()

if __name__ == "__main__" :
    main()
