from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def scrape_stock_data():
    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()  # Or webdriver.Firefox() if using Firefox
    driver.get("https://portal.tradebrains.in/index/MIDCAP50/heatmap")
    
    # Wait for the page to load completely
    time.sleep(5)
    
    # Get page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
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
    
    # Close the browser
    driver.quit()
    
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
