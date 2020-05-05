import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import re
import os.path

bot = commands.Bot(command_prefix='!!', description='HaGaon HaMachane Reborn!')
bot.remove_command('help')

@bot.event
async def on_ready():
        print(f'Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers')
        
        cog_list = ['Text','HebrewDate', 'OldCommands', 'Help']
        
        for cog in cog_list:
                bot.load_extension(cog)

if (os.path.isfile(token.txt)): 
        token = open("token.txt", "r").read()
else:
        token = open("/hagaon/token.txt", "r").read()
bot.run(token.strip())
