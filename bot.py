### Imports
import requests
import random
import time
import os
import logging
import json
import sys

from dotenv import load_dotenv
from pathlib import Path

# Get .env file path FIRST
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

env_path = Path(application_path) / '.env'

# Load .env with specific path
load_dotenv(env_path)

### Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

file_handler = logging.FileHandler(os.path.join(application_path, 'bot.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

### Global variables
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

### Token control
if not AUTH_TOKEN:
    logger.error("AUTH_TOKEN environment variable is not set!")
    logger.error(f"Looking for .env file at: {env_path}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Application path: {application_path}")
    
    # Manual .env read attempt
    if env_path.exists():
        logger.error("Attempting manual .env read...")
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip().startswith('AUTH_TOKEN'):
                        logger.error(f"Found AUTH_TOKEN line: {repr(line.strip())}")
        except Exception as e:
            logger.error(f"Manual read failed: {e}")
    
    sys.exit(1)

### Functions
def send_post(channel):
    max_message_retry = 3
    attempts = 0

    payload = {
        "content" : channel["message"]
    }

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]

    headers = {
        "authorization": AUTH_TOKEN,
        "user-agent": random.choice(user_agents),
        "content-type": "application/json",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate",
        "connection": "keep-alive",
        "origin": "https://discord.com",
        "referer": f"https://discord.com/channels/{channel["channel_id"]}/{channel["channel_id"]}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-debug-options": "bugReporterEnabled",
        "upgrade-insecure-requests": "1"
    }

    while attempts < max_message_retry:
        try:
            res = requests.post(channel["url"], json=payload, headers=headers)

        except Exception as e:
            logger.info(f"{channel['channel_name']} Request error: {e}")
            break

        if res.status_code == 200:
            logger.info(f"{channel['channel_name']} Message has been sent: {res.status_code}")
            return True

        elif res.status_code == 401:
            logger.error(f"The token you have entered is wrong or expired. Please check the token: {res.status_code}")
            sys.exit(1)
        
        elif res.status_code == 403:
            logger.error(f"403 Forbidden: {res.text}")
            return "Forbidden"

        elif res.status_code == 429:
            try:
                retry_data = res.json()
                retry_after = retry_data.get("retry_after", 20)
                code = retry_data.get("code", 0)

                logger.warning(f"{retry_data}")

                if code == 20016:
                    # Slowmode active
                    if retry_after > 300:
                        logger.warning(f"Wait is more than 5 mins. Waiting for 300 seconds anyway.")
                        time.sleep(300)
                        attempts += 1
                        continue

                    attempts += 1
                    logger.warning(f"Slowmode is active in {channel['channel_name']}! Waiting for {retry_after:.2f} seconds.")
                    time.sleep(retry_after + 20)

                elif code == 20028:
                    long_wait = max(retry_after, 60)

                    if retry_after > 300:
                        logger.warning(f"Wait is more than 5 mins. Waiting for 300 seconds anyway.")
                        time.sleep(300)
                        attempts += 1
                        continue

                    attempts += 1
                    logger.warning(f"{channel['channel_name']} hit the write rate limit (code 20028). Wait time set to: {long_wait:.2f} seconds. Attempt: {attempts}")
                    time.sleep(long_wait)
                
                else:
                    attempts += 1
                    logger.error(f"Bot exceeded rate limit to channel: {channel['channel_name']}! Wait {retry_after:.2f} sec. Retry: {attempts}")
                    time.sleep(retry_after + 20)

            except Exception as e:
                logger.info(f"{channel['channel_name']} returned 429 but failed to parse JSON: {e}")
                break
                
        else:
            logger.info(f"{channel['channel_name']} Error: {res.status_code}")
            break

    logger.info(f"{channel['channel_name']} Message couldn't send. Maximum retry limit of: ({max_message_retry}) reached.")
    return None
    

def update_channels_json(file_name, channels):
    with open(file_name, "w", encoding = "utf-8") as f:
        json.dump(channels, f, indent = 4, ensure_ascii = False)

def main_code():
    try:
            print("--" * 30)
            sleep = int(input("How many seconds should bot wait before sending texts again: "))

    except ValueError:
            logger.error("Please enter a valid number for sleep time.")
            sys.exit(1)

    print("Available files in the current directory:")

    for file in os.listdir():
        if file.endswith(".json"):
            print(f"{file}")

    print("--" * 30)
    file_name = input("Enter the file name you want to use: ")
    print("--" * 30)

    try:
        if file_name.endswith(".json"):
            with open(file_name, "r", encoding = "utf-8") as f:
                channels = json.load(f)
        else:
            logger.error("Please enter the file name with .json extension (e.g. channels.json).")
            sys.exit(1)

    except FileNotFoundError:
        logger.error(f"File {file_name} not found. Please check the file name and try again.")
        sys.exit(1)

    while True:
        for channel in channels[:]:
            interval = random.uniform(10, 20)
            roll = random.randint(0, 100)

            if channel['chance'] >= roll:
                success = send_post(channel)

                if success == "Forbidden":
                    logger.info(f"Erasing {channel['channel_name']} because code 403.")
                    channels.remove(channel)
                    update_channels_json(file_name, channels)
                    continue

                elif success == True:
                    logger.info(f"The next message will be sent in {interval:.2f} seconds.")

                else:
                    logger.warning(f"Failed to send message to {channel['channel_name']}, skipping this time.")

            else:
                logger.info(f"Roll number {roll} came up; skipping post for: {channel['channel_name']} this time.")

            time.sleep(interval)

        logger.info(f"All messages have been sent. The script will wait for {(sleep)/60:.2f} minutes before continuing.")
        time.sleep(sleep)
            

def add_channel():
    print("Available files in the current directory:")

    for file in os.listdir():
        if file.endswith(".json"):
            print(f"{file}")

    print("--" * 30)
    file_name = input("Enter the file name that you want to add new channel: ")
    print("--" * 30)

    try:
        if file_name.endswith(".json"):
            with open(file_name, "r", encoding="utf-8") as f:
                channels = json.load(f)
        else:
            logger.error("Please enter the file name with .json extension (e.g. channels.json).")
            sys.exit(1)  
    except FileNotFoundError:
        logger.error(f"File {file_name} not found. Please check the file name and try again.")
        sys.exit(1)

    channel_name = input("Please enter the discord channel's name: ").strip()
    channel_id = int(input("Please enter the discord channel id: ").strip())
    channel_message = input("Please enter the message in 1 line (use \\n for new lines): ").replace("\\n", "\n")
    message_chance = int(input("Please enter the chance of text (must be between 0 - 100): ").strip())

    new_channel = {
        "channel_name": channel_name,
        "url": f"https://discord.com/api/v9/channels/{channel_id}/messages",
        "channel_id": channel_id,
        "message": channel_message,
        "chance": message_chance
    }

    channels.append(new_channel)

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(channels, f, indent=4, ensure_ascii=False)

    logger.info(f"Added new channel {channel_name} to {file_name}.")


### Main code
if __name__ == "__main__":
    try:
        choice = int(input("Welcome to the Selfbot!\nPlease enter what you want do do:\n1. Start the bot.\n2. Add new channel\nWhat would you like to do: "))
        
        match choice:
            case 1:
                main_code()
            case 2:
                add_channel()
            case _:
                print("Please choose either 1 or 2")  
                sys.exit(1)
    
    except Exception as e:
        logger.exception(f"Program crashed with an error: {e}")
        input("An error occurred. For details check the log file. Press enter to close the script...")