import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()

# Constants
URL = "https://www.tori.fi/koko_suomi?q=guitar+hero&cg=0&w=3&st=s&st=g&ca=18&l=0&md=th"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
USER_ID = os.getenv('USER_ID')  # Telegram user ID
POSTED_ITEMS_FILE = "posted_items.txt"  # File to store URLs of posted items
TIME_FRAME_MINUTES = 120  # Check for items posted within the last 60 minutes
# Define the log file path
LOG_FILE_PATH = "tori2telegram.log"

# Finnish month abbreviations to numeric mapping
FIN_MONTHS = {
    'tam': 1, 'hel': 2, 'maa': 3, 'huh': 4,
    'tou': 5, 'kes': 6, 'hei': 7, 'elo': 8,
    'syy': 9, 'lok': 10, 'mar': 11, 'jou': 12
}

# Initialize logging with configurable log level
log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)


# Log rotation function
def rotate_log_file(log_file_path, max_size=10, max_files=3):
    """
    Rotates the log file and maintains only a specified number of old log files.

    Args:
    log_file_path (str): The path to the current log file.
    max_size (int): The maximum size of the log file in megabytes before rotation. Defaults to 10 MB.
    max_files (int): The maximum number of old log files to keep. Defaults to 3.

    This function first checks if the current log file exceeds the max_size (in MB). 
    If it does, the file is rotated. Then, it deletes older log files, keeping only the latest max_files number of log files.
    """

    # Convert max_size from megabytes to bytes for comparison
    max_size_bytes = max_size * 1024 * 1024

    # Check if the current log file exists and its size exceeds the maximum size
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) >= max_size_bytes:
        logging.info("Rotating log file")

        # Rotate the current log file by renaming it with a timestamp
        new_log_file_path = f"{log_file_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        os.rename(log_file_path, new_log_file_path)

        # Find all rotated log files (those with the .bak extension)
        rotated_files = sorted(glob(f"{log_file_path}_*.bak"))

        # Keep only the latest 'max_files' number of log files, delete the rest
        if len(rotated_files) > max_files:
            for file_to_delete in rotated_files[:-max_files]:
                logging.info(f"Removing old log file: {file_to_delete}")
                os.remove(file_to_delete)


def load_posted_items():
    """
    Loads the list of already posted items from a file.

    Returns:
    set: A set of URLs of already posted items.
    """
    if os.path.exists(POSTED_ITEMS_FILE):
        with open(POSTED_ITEMS_FILE, 'r') as file:
            return set(file.read().splitlines())
    return set()

def add_posted_item(url, posted_items):
    """
    Adds a new item's URL to the file of posted items.

    Args:
    url (str): The URL of the item to add.
    posted_items (set): The set of URLs of already posted items.
    """
    if url not in posted_items:  # Check if the URL is not already in the set
        posted_items.add(url)    # Add the URL to the set
        with open(POSTED_ITEMS_FILE, 'a') as file:
            file.write(url + '\n')

def parse_time(time_str):
    """
    Parses and formats the given Finnish time string into a datetime object.

    Args:
    time_str (str): The time string to parse.

    Returns:
    datetime: The parsed datetime object or None if parsing fails.
    """
    now = datetime.now()
    original_time_str = time_str
    time_str = ' '.join(time_str.split()).lower()

    logging.debug(f"Original time string: {original_time_str}, Processed time string: {time_str}")

    if 'tänään' in time_str:
        date = now.date()
        time_part = time_str.split()[-1]
    elif 'eilen' in time_str:
        date = (now - timedelta(days=1)).date()
        time_part = time_str.split()[-1]
    else:
        try:
            day, fin_month, time_part = time_str.split()
            month_index = FIN_MONTHS[fin_month]
            date = datetime(now.year, month_index, int(day))
        except (ValueError, KeyError) as e:
            logging.error(f"Unrecognized date format: {time_str}, Error: {e}")
            return None

    combined_datetime = datetime.combine(date, datetime.strptime(time_part, "%H:%M").time())
    logging.debug(f"Combined datetime: {combined_datetime}")
    return combined_datetime


def post_to_telegram(item):
    """
    Posts a given item to Telegram.

    Args:
    item (dict): The item to post.
    """
    title, price, time_posted, item_url, image_url = item["title"], item["price"], item["time_posted"], item["url"], item["image"]
    message = f"New item: {title}\nPrice: {price}\nTime: {time_posted}\nURL: {item_url}\n{image_url}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={USER_ID}&text={message}"
    try:
        response = requests.post(url)
        response.raise_for_status()
        logging.info("Successfully posted message to user %s", USER_ID)
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error occurred: {e}")



def fetch_and_process_items(posted_items):
    """
    Fetches and processes items from the specified URL.

    Args:
    posted_items (set): The set of URLs of already posted items.

    Returns:
    list: A list of new items found.
    """
    with requests.Session() as session:  # Using requests.Session for better performance
        try:
            response = requests.get(URL)
            soup = BeautifulSoup(response.content, 'html.parser')
            item_rows = soup.find_all('a', class_='item_row_flex')
            new_items = []

            for row in item_rows:
                item_url = row['href']
                title_element = row.find('div', class_='li-title')
                price_element = row.find('p', class_='list_price')
                time_element = row.find('div', class_='date_image')
                image_element = row.find('img', class_='item_image')

                if title_element and time_element:
                    title = title_element.text.strip()
                    price = price_element.text.strip() if price_element else 'Price not available'
                    time_posted = time_element.text.strip()
                    parsed_time = parse_time(time_posted)
                    if not parsed_time or item_url in posted_items:
                        continue
                    image_url = image_element['src'] if image_element else 'No image available'
                    if parsed_time > datetime.now() - timedelta(minutes=TIME_FRAME_MINUTES):
                        new_items.append({"title": title, "price": price, "time_posted": parsed_time, "url": item_url, "image": image_url})
                        add_posted_item(item_url, posted_items)  # Add the item URL to the set and file

            return new_items
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching items: {e}")
            return []


def main():
    # Rotate and manage log file at the start
    rotate_log_file("tori2telegram.log")

    posted_items = load_posted_items()

    while True:
        try:
            new_items = fetch_and_process_items(posted_items)
            for item in new_items:
                logging.info(f"Processing item: {item['title']}")
                post_to_telegram(item)
                add_posted_item(item['url'], posted_items)

        except Exception as e:
            logging.error("Script failed: %s", e)

        logging.info("Sleeping for 1 minute.")
        time.sleep(60)

if __name__ == "__main__":
    main()
