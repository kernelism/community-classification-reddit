# Constants for WebDriver configuration
CHROME_OPTIONS = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
DRIVER_PATH_ENV = "DRIVER_PATH"

# Reddit scraping constants
BASE_URL = "https://reddit.com/"
POST_LINK_ATTR = {"slot": "full-post-link"}

# File and directory paths
CHECKPOINT_FILE = 'checkpoint.json'
DATA_DIR = "../new/data"
GRAPHS_DIR = "../new/graphs"
SUBREDDITS_FILE = "subreddits.json"
ALL_SCRAPED_FILE = "../all_scraped.txt"
