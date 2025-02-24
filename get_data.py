from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import psycopg2
from datetime import datetime  # Import datetime for timestamp

# PostgreSQL Connection Configuration
DB_CONFIG = {
    "dbname": "maxpain",
    "user": "zeus",
    "password": "USmc1775!",
    "host": "localhost",
    "port": 5432
}

def get_watched_tickers():
    """Fetch tickers from maxpain.watched_tickers"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('SELECT "Ticker" FROM maxpain.watched_tickers;')
        tickers = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return tickers
    except Exception as e:
        print(f"Database error: {e}")
        return []

def insert_maxpain_data(ticker, maturity_date, max_pain, stock_price, hit_maxpain):
    """Insert data into maxpain.MaxPain table"""
    today_date = datetime.today().strftime('%Y-%m-%d')  # Get today's date
    current_time = datetime.today().strftime('%H-%M-%S')  # Get current time in HH-MM-SS format
    ticker_key = f"{ticker}_{maturity_date.replace('/', '-')}_{current_time}"  # Generate ticker_key (TICKER_YYYY-MM-DD_HH-MM-SS)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = """
        INSERT INTO maxpain."MaxPain" ("Ticker", "Date", "MaxPain", "Current Price", "Hit MaxPain", "Date Updated", "ticker_key")
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (ticker, maturity_date, max_pain, stock_price, hit_maxpain, today_date, ticker_key))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted: {ticker} | Date: {maturity_date} | Max Pain: {max_pain} | Stock Price: {stock_price} | Hit MaxPain: {hit_maxpain} | Date Updated: {today_date} | Ticker Key: {ticker_key}")
    except Exception as e:
        print(f"Insert error: {e}")

def scrape_maxpain():
    """Scrapes max pain values and stock price for only the first available maturity date"""
    tickers = get_watched_tickers()
    if not tickers:
        print("No tickers found in watched_tickers table.")
        return

    # Set up Selenium WebDriver (Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--incognito")  # Open in Incognito mode
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
    #options.add_argument("--user-data-dir=/tmp/selenium_user_data")  # Use a unique profile
    options.add_argument("--user-data-dir=/tmp/new_chrome_profile")


    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)  # Explicit wait

    driver.get("https://maximum-pain.com/options")
    time.sleep(3)  # Allow page to load

    for ticker in tickers:
        try:
            # Find the ticker input field and enter the ticker
            input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[formcontrolname="formTicker"]')))
            input_field.clear()
            input_field.send_keys(ticker)
            input_field.send_keys(Keys.RETURN)
            time.sleep(3)  # Wait for page to update

            # Locate the first maturity date from the dropdown
            maturity_select = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[formcontrolname="formMaturity"]')))
            first_option = maturity_select.find_elements(By.TAG_NAME, "option")[0]  # Get the first maturity date
            maturity_date = first_option.get_attribute("value").strip()

            # Select the first maturity date
            driver.execute_script("arguments[0].selected = true;", first_option)
            first_option.click()
            time.sleep(2)  # Allow the page to update based on selection

            # Locate the "Max Pain" value from the summary table
            try:
                max_pain_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//app-maxpain//table/caption/b[contains(text(), "Max Pain")]'))
                )
                max_pain_text = max_pain_element.text.split("$")[-1]  # Extract value after "$"
                max_pain_value = float(max_pain_text.strip())
            except Exception:
                print(f"Skipping {ticker} ({maturity_date}): Unable to locate Max Pain value.")
                continue

            # Locate the stock price from the summary table
            try:
                stock_price_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//table[@class="table table-striped table-bordered"]/tbody/tr/td[2]'))
                )
                stock_price_text = stock_price_element.text.replace("$", "").strip()  # Extract value after "$"
                stock_price = float(stock_price_text)
            except Exception:
                print(f"Skipping {ticker} ({maturity_date}): Unable to locate Stock Price.")
                stock_price = None  # If not found, default to None

            # Determine if the stock price is within $0.10 of the Max Pain value
            if stock_price is not None and abs(stock_price - max_pain_value) <= 0.10:
                hit_maxpain = True
            else:
                hit_maxpain = False

            # Insert into database if both values are valid
            if max_pain_value is not None and stock_price is not None:
                insert_maxpain_data(ticker, maturity_date, max_pain_value, stock_price, hit_maxpain)
            else:
                print(f"Skipping {ticker} ({maturity_date}): Missing data.")

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    driver.quit()

# Run the scraper
if __name__ == "__main__":
    scrape_maxpain()

