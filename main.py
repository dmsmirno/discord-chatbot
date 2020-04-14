# Work with Python 3.6
import discord
import os
import random
import random
import asyncio
import aiohttp
import json
import time
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import csv
style.use("fivethirtyeight")


#Personal token for use with bot
TOKEN = 'XXXXXXXXXXXXXXX'

#initialize Bot
bot = commands.Bot(command_prefix='?')

#Function takes server variable as arg, returns 
#user statistics on the server (discord convention names servers guilds)
# returns number of online, offline and busy server members
def community_report(guild):
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        elif str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline

#Function active when the bot is active, 
# Records user metrics over a 5 hour period
# Stores metrics into an accompanying .csv file
# When called, the command also provides a graph of user data in discord chat
async def background_metrics():
    await bot.wait_until_ready()
    global my_server
    my_server = bot.get_guild('XXXXXX')
    while not bot.is_closed():
        try:
            online, idle, offline = community_report(my_server)
            with open("usermetrics.csv","a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")
                f.close()

            with open("usermetrics.csv","r+") as f:
                reader = csv.reader(f)
                lines = len(list(reader))
                if(lines > 300):
                    f.close()
                    with open("usermetrics.csv", "w") as f:
                        f.truncate()
                        f.close()
            plt.clf()
            df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df['date'] = pd.to_datetime(df['time'],unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1,  inplace=True)
            df.set_index("date", inplace=True)
            df['online'].plot()
            plt.legend()
            plt.savefig("online.png")

            await asyncio.sleep(60)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(10)

#Main function that registers user input and responds in chat
@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    global my_server
    my_server = bot.get_guild('XXXXXXXXX')
    #return server member count
    if "cbot how many members" == message.content.lower():
        await message.channel.send(f"```{my_server.member_count}```")
    #greet user saying hello
    elif message.content.startswith('cbot hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
    #returns a graph of server user statistics and a count of online/idle/offline users
    elif message.content.lower() == "cbot server report":
        online, idle, offline = community_report(my_server)
        await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")
        file = discord.File("online.png", filename="online.png")
        await message.channel.send("online.png", file=file)
    #fun eightball function that gives a random answer to any question
    elif message.content.startswith(("cbot 8b", "cbot8b", "cbot eightball")):
        possible_responses = [
            'That is a resounding no',
            'It is quite possible',
            'Definitely',
            'Impossible',
            'Perhaps, but not today',
            'No',
            'Yes'
        ]
        await message.channel.send(random.choice(possible_responses) + ", " + message.author.mention)

#check bot in terminal when logging in
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#run loop of recording server usage stats
bot.loop.create_task(background_metrics())
#run bot
bot.run(TOKEN)