import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up your web driver (ensure you have ChromeDriver installed and in your PATH)
import os
from dotenv import load_dotenv

login_url = "https://app.acquire.com/"  # Replace with the actual login URL
# Load environment variables from .env file
load_dotenv()


MAX_BUDGET_IN_K = 10

# Get login credentials from environment variables
username = os.getenv('ACQUIRE_USERNAME')
password = os.getenv('ACQUIRE_PASSWORD')

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Optional: Disable GPU acceleration
chrome_options.add_argument("--window-size=1920,1080")  # Optional: Set window size

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                          options=chrome_options)

def login_and_navigate(driver):
    # Navigate to login page
    driver.get(login_url)

    # Find the email and password fields and log in
    driver.find_element(By.CSS_SELECTOR, 'input[inputmode="email"]').send_keys(username)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)

    driver.find_element(By.CLASS_NAME, 'btn-main').click()

    # Wait for login to complete (adjust the selector and wait time as needed)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "buyer-listings-tabs")))

    # Navigate to the landing page with products
    landing_page_url = "https://app.acquire.com/all-listing"  # Replace with the actual URL
    driver.get(landing_page_url)


def scroll_and_extract_product_links(driver):
    # Scroll down to load all products
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time as necessary
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extract product links
    product_links = []
    products = driver.find_elements(By.CSS_SELECTOR, "a.marketplace-card")  # Update with the correct CSS selector
    for product in products:
        link = product.get_attribute("href")
        # Check if the product value is less than $12k
        value_element = product.find_element(By.CSS_SELECTOR, "div.marketplace-info-item:nth-of-type(3) span.header-h3")
        if value_element:
            value_text = value_element.text.strip()
            if value_text.endswith('k'):
                try:
                    value = float(value_text[1:-1])  # Remove '$' and 'k', convert to float
                    if value <= MAX_BUDGET_IN_K:
                        link = product.get_attribute("href")
                        # Extract the product ID from the link
                        product_links.append(link + ":" + value_text)
                except ValueError:
                    pass
    
    # Print product links on console
    print("Product Links:")
    for index, link in enumerate(product_links, start=1):
        print(f"{index}. {link}")
    
    return product_links


def extract_product_details(driver):
    product_details = []
    # Load existing product IDs from JSON file
    try:
        with open('fetched_products.json', 'r') as f:
            fetched_products = json.load(f)
    except FileNotFoundError:
        fetched_products = []
        with open('fetched_products.json', 'w') as f:
            json.dump([], f)

    for link in product_links:
        product_id = link.split('startup/')[1].split('?')[0]

        # Check if the product_id has been fetched before
        if product_id not in fetched_products:
            driver.get(link)
         
            time.sleep(5)  # Allow the page to load

            # Extract product information
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            product_details.append({
                "Link": link,
                "Title": soup.select_one(".ma-review-wrap span.header-h4").get_text(strip=True) if soup.select_one(".ma-review-wrap span.header-h4") else "",
                "shortDesc": soup.select_one("span.body-p1-medium.c-smoke").get_text(strip=True) if soup.select_one("span.body-p1-medium.c-smoke") else "",
                "asking_price": soup.select_one("span.p-relative").get_text(strip=True) if soup.select_one("span.p-relative") else "",
                "description": soup.select_one(".mt-40 span.public-info-block-item__description").get_text(strip=True) if soup.select_one(".mt-40 span.public-info-block-item__description") else "",
                "ttm-revenue": soup.select_one("div.project-info-item:nth-of-type(1) span.body-p2-medium").get_text(strip=True) if soup.select_one("div.project-info-item:nth-of-type(1) span.body-p2-medium") else "",
                "ttm-profit": soup.select_one("div.project-info-item:nth-of-type(2) span.body-p2-medium").get_text(strip=True) if soup.select_one("div.project-info-item:nth-of-type(2) span.body-p2-medium") else "",
                "last-month-revenue": soup.select_one("div:nth-of-type(3) span.body-p2-medium.c-smoke").get_text(strip=True) if soup.select_one("div:nth-of-type(3) span.body-p2-medium.c-smoke") else "",
                "last-month-profit": soup.select_one("div.project-info-item:nth-of-type(4) span.body-p2-medium").get_text(strip=True) if soup.select_one("div.project-info-item:nth-of-type(4) span.body-p2-medium") else "",
                "company": soup.select_one(".features-info-editor span.public-info-block-item__description").get_text(strip=True) if soup.select_one(".features-info-editor span.public-info-block-item__description") else "",
                "tech-stack": soup.select_one("div.public-info-block-item:nth-of-type(5)").get_text(strip=True) if soup.select_one("div.public-info-block-item:nth-of-type(5)") else "",
                "customers": soup.select_one("div.metrics-tile:nth-of-type(1) div.special-metrics").get_text(strip=True) if soup.select_one("div.metrics-tile:nth-of-type(1) div.special-metrics") else "",
                "arr": soup.select_one("div.metrics-tile:nth-of-type(2) div.special-metrics").get_text(strip=True) if soup.select_one("div.metrics-tile:nth-of-type(2) div.special-metrics") else "",
                "AGR": soup.select_one("div:nth-of-type(3) div.special-metrics").get_text(strip=True) if soup.select_one("div:nth-of-type(3) div.special-metrics") else "",
                "traction": soup.select_one("span.highlight-card__description").get_text(strip=True) if soup.select_one("span.highlight-card__description") else "",
            })
            # Append the product_id to the fetched_products.json file
            fetched_products.append(product_id)
        else:
            print(f"Skipping product {product_id} as it has been fetched before.")     
    with open('fetched_products.json', 'w') as f:
        json.dump(fetched_products, f)
    return product_details


def update_google_sheet(product_details):
    # Write product details to DataFrame
    df = pd.DataFrame(product_details)

    # Set up Google Sheets API credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'service_account.json'  # Replace with your service account file path
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Create Google Sheets API service
    service = build('sheets', 'v4', credentials=creds)

    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    
    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID not found in .env file")

    # Get the current sheet data to determine where to append
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Sheet1').execute()
    current_data = result.get('values', [])
    next_row = len(current_data) + 1

    # Specify the range where you want to append the data
    RANGE_NAME = f'Sheet1!A{next_row}'

    # Prepare the data from the DataFrame
    values = df.values.tolist()

    # Prepare the request body
    body = {
        'values': values
    }

    # Make the API request to append to the sheet
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body,
        insertDataOption='INSERT_ROWS'
    ).execute()

    print(f"{result.get('updates').get('updatedRows')} rows appended to the Google Sheet.")

# Add a comment explaining the main steps of the script
# 1. Log in and navigate to the desired page
# 2. Scroll and extract product links
# 3. Extract product details from each link
# 4. Update the Google Sheet with the extracted data
# 5. Close the web driver

login_and_navigate(driver)
product_links = scroll_and_extract_product_links(driver)

# # Call the function to extract product details
product_details = extract_product_details(driver)

# update_google_sheet(product_details)
update_google_sheet(product_details)

# Close the web driver
driver.quit()