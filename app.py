from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def scrape_stock_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://portal.tradebrains.in/index/MIDCAP50/heatmap")
        page.wait_for_timeout(10000)  # Wait for content to load
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    
    # Find all stock cards by their structure in the HTML
    stock_data = []
    for card in soup.select("a[target='_self']"):
        try:
            # Clean the change_percentage string
            change_percentage = card.select_one("p.d-flex.justify-content-end").text.strip().replace("%", "").replace("+", "").strip()
            symbol = card.select_one("p.fs-16-14.fw-600").text.strip()
            price = card.select_one("p.fs-14-12").text.strip().replace("₹", "").strip()
            
            # Convert to float after cleaning
            stock_data.append({
                "name": symbol,
                "value": abs(float(change_percentage)),  # Use absolute change for size
                "change": change_percentage,
                "price": price
            })
        except (AttributeError, ValueError):
            # Skip cards that don't match the expected structure or have conversion issues
            continue
    print(stock_data)
    return stock_data


@app.route('/data')
def data():
    stock_data = scrape_stock_data()
    return jsonify(stock_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
