# README for Telegram Bot Python Script

## Overview

This Python script is designed to scrape and post items from a Finnish online marketplace (https://www.tori.fi) to a specified Telegram user. It includes features such as log file rotation and customizable settings for item posting time frame and script execution intervals.

## Features

- **Automated Web Scraping**: Retrieves item details from a specific URL.
- **Telegram Notifications**: Sends item updates to a Telegram user.
- **Configurable Time Frame and Sleep Interval**: Customizable settings for item posting time frame and execution intervals.
- **Log File Rotation**: Automatically manages log file sizes, rotating them when they exceed a specified size.
- **Continuous Operation**: Designed to run continuously in the background.

## Prerequisites

- Python 3.6 or later.
- PIP for package installation.

## Setting Up the Telegram Bot

To receive notifications, you need to create a Telegram bot and obtain a token:

1. Open Telegram and search for 'BotFather'.
2. Start a conversation with BotFather and create a new bot by sending `/newbot`.
3. Follow the instructions to name your bot and get a username.
4. BotFather will provide a token. Copy this token.
5. Find your Telegram user ID by messaging `@userinfobot`.
6. Create a `.env` file in the project directory with the following content:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   USER_ID=your_telegram_user_id
   LOG_LEVEL=DEBUG_or_INFO
   SLEEP_INTERVAL=define_seconds
   ```

## Installation

1. **Clone the Repository (if applicable)**:
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file with the following content:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   USER_ID=your_telegram_user_id
   LOG_LEVEL=DEBUG  # Can be INFO, WARNING, ERROR, CRITICAL
   SLEEP_INTERVAL=120  # Time in seconds for script sleep interval
   ```

## Running the Script

Execute the script using the following command:

```bash
nohup python3 tori2telegram.py > tori2telegram.log 2>&1 &
```

This command runs the script in the background, detaching it from the terminal, and logs output to `tori2telegram.log`.

## Stopping the Script

To stop the running script:

1. **Find the Process ID (PID)**:
   ```bash
   ps -ef | grep tori2telegram.py
   ```

2. **Terminate the Process**:
   ```bash
   kill [PID]
   ```

   Replace `[PID]` with the actual process ID.

## Configuration

### Time Frame Configuration

- `TIME_FRAME_MINUTES`: Set within the script to define the window for considering new items.

### Script Sleep Interval

- `SLEEP_INTERVAL`: Defined in the `.env` file, this variable sets the pause duration (in seconds) between execution cycles.

### Log File Rotation

- The script includes functionality to automatically rotate the log file `tori2telegram.log` when it reaches a specified size limit, keeping the log management efficient.

## Log File Management

- Regularly check the size of `tori2telegram.log`. The script rotates this file automatically, but be mindful of the disk space used by archived logs.

## Important Notes

- Adjust the sleep interval with caution to avoid server rate-limiting or high resource consumption.
