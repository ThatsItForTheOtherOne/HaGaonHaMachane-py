import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import datetime
import hdate
import json
from urllib.request import urlopen


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/calendars"
        self.change_status.start()

    @tasks.loop(hours=1)
    async def change_status(self):
        sefaria_obj = json.load(urlopen(self.api_url))
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        status_string = f"""
                    {date.hebrew_date}
                    | {self.bot.command_prefix}help
                    | Today's Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    | Today's Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    """
        status_string = status_string.replace("\n", " ")
        status_string = status_string.replace("\r", " ")
        status_string = status_string.replace("                    ", "")
        print(f"The status string is {len(status_string)} chars")
        game = discord.Game(status_string)
        await self.bot.change_presence(status=discord.Status.online, activity=game)


def setup(bot):
    bot.add_cog(Status(bot))
