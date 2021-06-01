import argparse
import asyncio
from os import getenv as os_getenv
from dotenv import load_dotenv
import json
from mcstatus import MinecraftServer as MCServer

import discord
from discord.ext import tasks

load_dotenv()

config = {}
def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f)

try:
    with open("config.json") as f:
        config = json.load(f)
except:
    save_config()

parser = argparse.ArgumentParser(description='Watches a specific minecraft server ip and displays it.')
parser.add_argument('-ip')
parser.add_argument('-port', type=int)
parser.add_argument('-query', action='store_true')
args = parser.parse_args()

ip = args.ip or "127.0.0.1"
port = args.port or 25565
full = ip + ("" if port==25565 else str(port))
server = MCServer(ip, port)
query = args.query or False

client = discord.Client()

@client.event
async def on_ready():
    print("Watching IP: {0} on port {1}".format(ip, port))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.permissions_in(message.channel).administrator:
        if message.content == "/focus":
            config[message.guild.id] = message.channel.id
            save_config()
            await message.channel.send("Bruh.")
            await message.delete()

@tasks.loop(seconds = 10)
async def update():
    while True:
        for guild in client.guilds:
            channelid = config.get(str(guild.id))
            if not channelid:
                continue
            channel = client.get_channel(channelid)
            if not channel:
                continue
            if not query:
                try:
                    status = server.status()
                    txt = "[{0}] - Players: {1}/{2}".format(full, status.players.online, status.players.max)
                    for ply in status.players.sample:
                        txt += "\n{0}".format(ply.name)
                    await channel.edit(topic=txt)
                except Exception as e:
                    print(e)
            else:
                raise NotImplementedError
                #query = server.query()
                #await channel.edit(topic=("[{0}] - Players: {1}/{2}".format(full, plys, maxplys)))
        await asyncio.sleep(10)
update.start()
client.run(os_getenv("TOKEN"))
