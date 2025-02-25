# MaxPain Scraper

## Overview
This project is a Python-based web scraper that retrieves Max Pain values and stock prices for watched tickers from [maximum-pain.com](https://maximum-pain.com/options). The script uses Selenium to interact with the website, extracts relevant financial data, and stores the results in a PostgreSQL database.

## Features
- Fetches a list of tickers from the `maxpain.watched_tickers` database table.
- Uses Selenium WebDriver (Chrome) to interact with the website.
- Extracts the first available maturity date, Max Pain value, and stock price.
- Determines whether the stock price is within $0.10 of the Max Pain value.
- Inserts the extracted data into the `maxpain.MaxPain` table.
- Runs in headless mode for automated execution.

## Requirements
- Python 3
- Google Chrome & ChromeDriver
- PostgreSQL
- Required Python Packages:
  - `selenium`
  - `psycopg2`

## Installation
1. Install the required Python packages:
   ```sh
   pip install selenium psycopg2
   ```
2. Download and install [Google Chrome](https://www.google.com/chrome/).
3. Download the appropriate version of [ChromeDriver](https://chromedriver.chromium.org/downloads) and add it to your system's PATH.
4. Set up a PostgreSQL database and update the `DB_CONFIG` dictionary in the script with your database credentials.

## Configuration
### Database Connection
Modify the `DB_CONFIG` dictionary in the script to match your PostgreSQL settings:
```python
DB_CONFIG = {
    "dbname": "maxpain",
    "user": "zeus",
    "password": "your_password_here",
    "host": "localhost",
    "port": 5432
}
```

### Selenium WebDriver
Ensure ChromeDriver is installed and accessible in your system's PATH.
The script configures the Chrome WebDriver as follows:
```python
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--incognito")  # Open in Incognito mode
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
options.add_argument("--user-data-dir=/tmp/new_chrome_profile")
```

## Usage
Run the scraper using:
```sh
python scraper.py
```
The script will:
1. Connect to the PostgreSQL database and fetch watched tickers.
2. Open the [maximum-pain.com](https://maximum-pain.com/options) website using Selenium.
3. Enter each ticker, retrieve the first maturity date, Max Pain value, and stock price.
4. Determine if the stock price is within $0.10 of the Max Pain value.
5. Insert the extracted data into the `maxpain.MaxPain` table.
6. Close the browser session.

## Database Tables
### `maxpain.watched_tickers`
| Column  | Type  |
|---------|-------|
| Ticker  | TEXT  |

### `maxpain.MaxPain`
| Column         | Type    |
|---------------|---------|
| Ticker        | TEXT    |
| Date          | TEXT    |
| MaxPain       | FLOAT   |
| Current Price | FLOAT   |
| Hit MaxPain   | BOOLEAN |
| Date Updated  | TEXT    |
| ticker_key    | TEXT    |

## Error Handling
- If an error occurs during scraping, it will be logged to the console.
- If a ticker is missing data, it will be skipped.

## License
This project is licensed under the MIT License.

