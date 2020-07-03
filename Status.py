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
        self.changeStatus.start()

    async def currentHebrewDate(self):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        return date.hebrew_date

    async def currentParasha(self):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        parashaStr = " ".join(("Parashat", date.parasha))
        return parashaStr

    @tasks.loop(hours=1)
    async def changeStatus(self):
        sefaria_obj = json.load(urlopen(self.api_url))
        game = discord.Game(
            "".join(
                (
                    self.bot.command_prefix,
                    "help | The date is ",
                    await self.currentHebrewDate(),
                    " | Today's parasha: ",
                    sefaria_obj["calendar_items"][0]["displayValue"]["en"],
                    " | Today's Haftarah: ",
                    sefaria_obj["calendar_items"][1]["displayValue"]["en"],
                )
            )
        )
        await self.bot.change_presence(status=discord.Status.online, activity=game)


def setup(bot):
    bot.add_cog(Status(bot))
