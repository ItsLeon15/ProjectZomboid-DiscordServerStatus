# Project Zomboid RCON Discord Bot (Server Status)

A simple Discord Bot for monitoring a Project Zomboid server via RCON. The bot connects to your server, get's the status and posts an update in a specified Discord channel.

## Example output
![image](https://github.com/user-attachments/assets/13b5d61e-6b1b-43dd-b41c-262ba9d77734)

## Features
- Server Status Monitoring (Tracks if the server is online or offline)
- Player Count (Shows the number of connected players)
- Options Parsing (Customize what options are shown like map name, max players, server name)

## Requirements (Dependencies)
- Python 3.9+
- Discord.py (pip install discord.py)

## Installation
### 1: Clone the repo
```
git clone https://github.com/ItsLeon15/ProjectZomboid-DiscordServerStatus.git
cd ProjectZomboid-DiscordServerStatus
```
### 2: Install dependencies
```
pip install discord.py
```
### 3: Configure the bot
Edit the `config.json` file with your settings:
```
{
  "rconIP": "<your-server-ip>",
  "rconPort": 27015,
  "rconPassword": "<your-rcon-password>",
  "notifyChannel": <your-discord-channel-id>,
  "botToken": "<your-discord-bot-token>"
}
```
### 4: Run the bot
`python main.py`
