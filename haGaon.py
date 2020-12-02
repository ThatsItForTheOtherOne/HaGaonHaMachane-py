import discord
from discord.ext import commands
import os.path
import aiosqlite

bot = commands.Bot(command_prefix="!!", description="HaGaon HaMachane Version 5.0")
bot.remove_command("help")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found! Check {bot.command_prefix}help!")


@bot.event
async def on_ready():
    if not os.path.isfile("haGaon.db"):
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        await cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS main(
        user_id TEXT,
        latitude TEXT,
        longitude TEXT,
        timezone TEXT,
        diaspora TEXT
        )
        """
        )
        await cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS translation(
        user_id TEXT,
        work TEXT,
        translation TEXT
        )
        """
        )
        await cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS default_translation(
        work TEXT,
        translation TEXT
        )
        """
        )
        await cursor.close()
        await db.close()
    print(f"Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers")

    cog_list = ["Text", "HebrewDate", "Help", "Status", "Zmanim"]

    for cog in cog_list:
        bot.load_extension(cog)


if os.path.isfile("token.txt"):
    token = open("token.txt", "r").read()
else:
    token = open("/hagaon/token.txt", "r").read()
bot.run(token.strip())
