import discord
from discord.ext import commands
import os.path
import sqlite3

bot = commands.Bot(command_prefix="!!", description="HaGaon HaMachane Version 1.4")
bot.remove_command("help")


@bot.event
async def on_ready():
    if not os.path.isfile("haGaon.db"):
        db = sqlite3.connect("haGaon.db")
        cursor = db.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS main(
        user_id TEXT,
        latitude TEXT,
        longitude TEXT,
        timezone TEXT,
        diaspora TEXT
    )"""
        )
    print(f"Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers")
    print(bot.guilds)

    cog_list = ["Text", "HebrewDate", "OldCommands", "Help", "Status", "Zmanim"]

    for cog in cog_list:
        bot.load_extension(cog)


if os.path.isfile("token.txt"):
    token = open("token.txt", "r").read()
else:
    token = open("/hagaon/token.txt", "r").read()
bot.run(token.strip())
