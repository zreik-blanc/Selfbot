# Discord Selfbot

> This Python bot automatically sends messages to specified Discord channels. It handles rate limits and slowmode, and supports logging.

---

## 🌟 Features

- Automatically send messages to designated channels  
- Chance-based message sending per channel  
- Random message intervals (10–20 seconds)  
- Rate limit and slowmode support  
- Automatically remove channels from JSON if access is denied  
- Logs all events to console and `bot.log`  

---

## 🛠 Requirements

- ```.env``` File is required to use the bot.
- ```AUTH_TOKEN=YOUR_DISCORD_TOKEN``` Replace it with your token.
- Other requirements are inside requirements.txt file

---

## Installation

- Clone the project from github page or use the link.

```bash
https://github.com/zreik-blanc/Selfbot.git
```
- Open the venv
```python
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS/Linux:
source .venv/bin/activate
```
- Use the command:
```python
pip install -r requirements.txt
```
- Setup the `.env` File and you are good to go!

---

## 📄 JSON File Structure

- The bot reads channel information and messages from a JSON file. Example:
```json
[
    {
        "channel_name": "general",
        "url": "https://discord.com/api/v9/channels/CHANNEL_ID_HERE/messages",
        "message": "Hello world!",
        "chance": 80,
    },
    {
        "channel_name": "random",
        "url": "https://discord.com/api/v9/channels/CHANNEL_ID_HERE/messages",
        "message": "Hi there!",
        "chance": 50,
    }
]
```
- You can use multiple json files in the directory the program will ask you to choose one.

---


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

---

## License

This project is licensed under [MIT](https://choosealicense.com/licenses/mit/) License

## ⚠️ Disclaimer

This bot is **intended for educational purposes only**. Using it for personal gain, spam, or any activity that violates Discord's Terms of Service (ToS) is strictly prohibited.  

- **Do NOT use this bot to send unsolicited messages or spam.**  
- **Do NOT use this bot for commercial purposes or to gain an unfair advantage.**  

By using this bot, you acknowledge that you are responsible for ensuring your actions comply with Discord's ToS and applicable laws. The author is **not responsible** for any misuse of this bot.
