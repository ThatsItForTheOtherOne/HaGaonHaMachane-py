import discord
from discord.ext import commands
import os.path

bot = commands.Bot(command_prefix="!!", description="HaGaon HaMachane Version 1.4")
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id}) on {len(bot.guilds)} servers")
    print(bot.guilds)

    cog_list = ["Text", "HebrewDate", "OldCommands", "Help", "Status"]

    for cog in cog_list:
        bot.load_extension(cog)


if os.path.isfile("token.txt"):
    token = open("token.txt", "r").read()
else:
    token = open("/hagaon/token.txt", "r").read()
bot.run(token.strip())
