import json
import os
import time
from typing import List, Dict

import click
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

import constants
import utils

load_dotenv()

class ScrapeReddit:
    def __init__(self, subreddit: str) -> None:
        options = Options()
        for arg in constants.CHROME_OPTIONS:
            options.add_argument(arg)
        self.driver = webdriver.Chrome(
            service=Service(os.getenv(constants.DRIVER_PATH_ENV)), options=options
        )
        self.postids: List[str] = []
        self.processed_ids: List[str] = []
        self.jsons: List[str] = []
        self.subreddit: str = subreddit
        self.checkpointed: bool = False

    def lazy_scroll(self) -> str:
        current_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        while True:
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == current_height:
                break
            current_height = new_height
        return self.driver.page_source

    def get_posts(self) -> None:
        self.driver.get(self.subreddit)
        self.driver.maximize_window()
        time.sleep(5)
        html = self.lazy_scroll()
        parser = BeautifulSoup(html, "html.parser")
        post_links = parser.find_all("a", constants.POST_LINK_ATTR)
        print(f"Found {len(post_links)} posts for subreddit {self.subreddit}")
        count = 1

        for post_link in post_links:
            post_id = post_link["href"].split("/")[-3]
            count += 1
            if post_id not in self.postids:
                self.postids.append(post_id)

    def save_state(self) -> None:
        with open(constants.CHECKPOINT_FILE, 'w') as file:
            state = {
                'processed_ids': self.processed_ids,
                'remaining_ids': [x for x in self.postids if x not in self.processed_ids]
            }
            json.dump(state, file)

    def load_state(self) -> None:
        try:
            with open(constants.CHECKPOINT_FILE, 'r') as file:
                state = json.load(file)
                self.processed_ids = state['processed_ids']
                self.postids = state['remaining_ids']
        except FileNotFoundError:
            self.processed_ids = []

    def get_data(self, postid: str) -> str:
        url = constants.BASE_URL + postid + ".json"
        self.driver.get(url)
        # self.driver.maximize_window()
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = soup.find("body").get_text()
        if "Too Many Requests" in text:
            return "429"
        return text

    def get_post_details(self) -> bool:
        if self.checkpointed:
            self.load_state()
            self.restart()
            self.checkpointed = False
            print("Resuming from checkpoint...")
        count = 1
        for postid in self.postids:
            if postid in self.processed_ids:
                continue
            print(f"Getting data for post {count} - {postid}")
            text = self.get_data(postid)
            if text == "429":
                self.save_state()
                self.destroy()
                self.checkpointed = True
                print("Error 429 encountered. Session stopped.")
                return self.checkpointed
            self.processed_ids.append(postid)
            self.jsons.append(text)
            count += 1

        return self.checkpointed

    def print_postids(self) -> None:
        print(self.postids)

    def restart(self) -> None:
        options = Options()
        for arg in constants.CHROME_OPTIONS:
            options.add_argument(arg)
        self.driver = webdriver.Chrome(
            service=Service(os.getenv(constants.DRIVER_PATH_ENV)), options=options
        )

    def destroy(self) -> None:
        self.driver.quit()

def process_subreddit(category, subreddit: str) -> Dict[str, str]:
    print("Scraping subreddit: ", subreddit)
    reddit = ScrapeReddit(subreddit=subreddit)
    subreddit_name = subreddit.split("/")[-3]
    try:
        reddit.get_posts()
        reddit.print_postids()
        while True:
            checkpointed = reddit.get_post_details()
            if not checkpointed:
                break
        relevant_post_info = []
        for json_string in reddit.jsons:
            try:
                parsed_json = json.loads(json_string)
                relevant_post_info.append(utils.get_post_info(parsed_json))
            except json.JSONDecodeError as e:
                print(e)
                continue
        utils.save_to_json(category, relevant_post_info, subreddit=subreddit_name)
    except Exception as e:
        print(e)
    finally:
        reddit.destroy()


@click.command()
@click.option('-d', '--duration', prompt='Scrape Duration', help='Duration to scrape for (month/year)')
@click.option('-ng', '--no-graph', is_flag=True, help='Do not generate graphs')
# @click.option('-rm', '--remove', is_flag=True, help='Remove outlier graphs')
def begin(duration, no_graph) -> None:
    if duration not in ["month", "year"]:
        raise ValueError("Duration must be either month or year")
    
    subreddits = utils.read_subreddits_from_json(constants.SUBREDDITS_FILE, duration)
    for category in subreddits:
        for subreddit in subreddits[category]:
            process_subreddit(category, subreddit)
    utils.saved_subreddits_in_txt(constants.DATA_DIR)
    if no_graph:
        return
    utils.save_graphs(subreddits)

    # Handling Git operations
    # if platform.system() == "Windows":
    #     subprocess.run(["powershell.exe", "Set-ExecutionPolicy", "Unrestricted"])
    #     subprocess.run(["powershell.exe", "./push_to_git.ps1"])  # or use a batch file
    # else:
    #     subprocess.run(["chmod", "+x", "./push_to_git.sh"])
    #     subprocess.run(["./push_to_git.sh"])


if __name__ == "__main__":
    begin()
