# 🛒 Amazon Product Scraper (Headless & Stealth Mode)

This Python script uses Selenium with an undetected Chrome driver to scrape product info from **Amazon India** based on a user’s search query. It’s all automated — from search to saving product images locally — and works headlessly to stay stealthy.

---

## 🚀 Features

- 💨 **Undetectable Automation**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: Uses `undetected_chromedriver` to avoid bot detection by Amazon.
- 🕶️ **Headless Operation**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: Runs in the background without opening a visible browser window.
- 📦 **Delivery Info Customization**&nbsp;&nbsp;&nbsp;: Optionally adds your PIN code to get location-relevant delivery details.
- 🧠 **Fully Generalized Search**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: Just type any product (literally *any*) and it adapts — no code changes needed.  
  > _This makes it super useful across various use-cases like price comparison, market research, or just casual tech flexing._
- 🖼️ **Image Downloader**           &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;: Saves product images for offline access or ML tasks.
- 📊 **Review + Price Info**        &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;: Pulls star ratings, review count, sold estimates, MRP, current price, and discounts.
- 🔗 **Direct Product Links**       &nbsp;&nbsp;&nbsp; &nbsp;: Each item includes a direct Amazon link for deep dive or buying later.

---

## 🔧 Requirements

Install the required packages before running:

```bash
pip install selenium undetected-chromedriver requests
```

Also make sure:
- Chrome Beta is installed (used in `binary_location`).
- You edit the path to your Chrome binary if it's different.

---

## 💻 How To Use

Run the script:

```bash
python script_name.py
```

Then:

1. Enter your product search term.
2. Optionally enter your PIN code for delivery customization.
3. Sit back &nbsp; it’ll scroll, scrape, and even download product images for you.

---

## 📁 Output

- Console output shows all details for each product.
- Product images are saved in a folder named after your search query.

---

## 🎯 Future Goals

- 📈 Extend support for scraping from more e-commerce sites like Flipkart, Meesho, Myntra, etc.
- 💬 Add a GUI or chatbot interface to make it beginner-friendly.
- 📦 Export scraped data to CSV/Excel for data analysis.

---

## ⚠️ Legal Note

This script is for **educational purposes only**. Always respect website's `robots.txt` policies and terms'n conditions of service.

---

## 🤝 Contributions

Pull requests and feature ideas are totally welcome. Let's make this into a full-blown multi-site scraper. 🔥
