import json
import discord
from rcon_client import RCONClient
from discord.ext import commands, tasks

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

with open('config.json') as f:
    config = json.load(f)

rcon_host = config["rconIP"]
rcon_port = config["rconPort"]
rcon_password = config["rconPassword"]
notify_channel_id = config["notifyChannel"]
bot_token = config["botToken"]

server_online = None
status_message_id = None

@tasks.loop(seconds=30)
async def check_server_status():
    """Check the server status and update Discord."""
    global server_online, status_message_id

    try:
        rcon = RCONClient(rcon_host, rcon_port, rcon_password)
        rcon.connect()
        players_response = rcon.send_command("players")
        print(f"Players Response: {players_response}")

        options_response = rcon.send_command("showoptions")
        if not options_response:
            raise Exception("Failed to retrieve server options.")

        map_value, max_players, public_name = "Unknown", "Unknown", "Unknown"
        for line in options_response.splitlines():
            if line.strip().startswith("* Map="):
                map_value = line.split("=")[1].split(";")[0].strip()
            elif line.strip().startswith("* MaxPlayers="):
                max_players = line.split("=")[1].strip()
            elif line.strip().startswith("* PublicName="):
                public_name = line.split("=")[1].strip()

        players_response = rcon.send_command("players")
        player_count = 0
        if "Players connected" in players_response:
            player_count = int(players_response.split(":")[0].split("(")[1].strip(")"))

        rcon.disconnect()

        if server_online is not True:
            server_online = True
            channel = bot.get_channel(notify_channel_id)
            if channel:
                embed = discord.Embed(
                    title="Project Zomboid Server Status",
                    description="The server is **Online**! 🎉",
                    color=discord.Color.green(),
                )
                embed.add_field(name="Server Name", value=public_name, inline=True)
                embed.add_field(name="Map", value=map_value, inline=True)
                embed.add_field(name="Players", value=f"{player_count}/{max_players}", inline=True)
                embed.add_field(name="Address", value=f"{rcon_host}:{rcon_port}", inline=False)
                embed.set_footer(text=f"Last updated: {discord.utils.utcnow()}")

                if status_message_id:
                    message = await channel.fetch_message(status_message_id)
                    await message.edit(embed=embed)
                else:
                    message = await channel.send(embed=embed)
                    status_message_id = message.id
            print("Server is online.")

    except Exception as e:
        print(e)
        if server_online is not False:
            server_online = False
            channel = bot.get_channel(notify_channel_id)
            if channel:
                embed = discord.Embed(
                    title="Project Zomboid Server Status",
                    description="The server is **Offline**. ❌",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Server Name", value="Unavailable", inline=True)
                embed.add_field(name="Map", value="Unavailable", inline=True)
                embed.add_field(name="Players", value="0/0", inline=True)
                embed.add_field(name="Address", value=f"{rcon_host}:{rcon_port}", inline=False)
                embed.set_footer(text=f"Last updated: {discord.utils.utcnow()}")

                if status_message_id:
                    message = await channel.fetch_message(status_message_id)
                    await message.edit(embed=embed)
                else:
                    message = await channel.send(embed=embed)
                    status_message_id = message.id
            print(f"Server is offline. Error: {e}")


@bot.event
async def on_ready():
    print("Bot is ready!")
    channel = bot.get_channel(notify_channel_id)
    if channel:
        await channel.send("🤖 Bot is online and monitoring the server.")
    check_server_status.start()


bot.run(bot_token)
