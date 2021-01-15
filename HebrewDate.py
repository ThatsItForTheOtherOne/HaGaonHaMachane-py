import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
from sendText import create_embed
import datetime
import hdate
import json
from urllib.request import urlopen
import aiohttp


class HebrewDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/calendars"
        self.events_str = ""
        self.grab_new_events.start()

    @tasks.loop(hours=1)
    async def grab_new_events(self):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                body = await response.text()
                sefaria_obj = json.loads(body)
            if date.is_holiday == False and 0 < date.omer_day < 50:
                self.events_str = f"""
                    Omer: {date.omer_day}
                    Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    Daf Yomi: {sefaria_obj["calendar_items"][2]["displayValue"]["en"]}
                    Mishnah Yomit: {sefaria_obj["calendar_items"][4]["displayValue"]["en"]}
                    Daily Rambam 1 Chapter: {sefaria_obj["calendar_items"][5]["displayValue"]["en"]}
                    Daily Rambam 3 Chapters: {sefaria_obj["calendar_items"][6]["displayValue"]["en"]}
                    Halakha Yomit: {sefaria_obj["calendar_items"][8]["displayValue"]["en"]}
                    """
            elif date.is_holiday == False:
                self.events_str = f"""
                    Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    Daf Yomi: {sefaria_obj["calendar_items"][2]["displayValue"]["en"]}
                    Mishnah Yomit: {sefaria_obj["calendar_items"][4]["displayValue"]["en"]}
                    Daily Rambam 1 Chapter: {sefaria_obj["calendar_items"][5]["displayValue"]["en"]}
                    Daily Rambam 3 Chapters: {sefaria_obj["calendar_items"][6]["displayValue"]["en"]}
                    Halakha Yomit: {sefaria_obj["calendar_items"][8]["displayValue"]["en"]}
                    """
            else:
                self.events_str = f"""
                    Holiday: {date.holiday_description}
                    Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    Daf Yomi: {sefaria_obj["calendar_items"][2]["displayValue"]["en"]}
                    Mishnah Yomit: {sefaria_obj["calendar_items"][4]["displayValue"]["en"]}
                    Daily Rambam 1 Chapter: {sefaria_obj["calendar_items"][5]["displayValue"]["en"]}
                    Daily Rambam 3 Chapters: {sefaria_obj["calendar_items"][6]["displayValue"]["en"]}
                    Halakha Yomit: {sefaria_obj["calendar_items"][8]["displayValue"]["en"]}
                    """

    @commands.command(name="hebrewDate")
    async def hebrew_date(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        await create_embed(ctx, date.hebrew_date)

    @commands.command(name="events")
    async def events_today(self, ctx):
        await create_embed(ctx, self.events_str)

    @commands.command(name="dateToHebrew")
    async def date_to_hebrew(self, ctx, year, month, day):
        gregorian_date = datetime.datetime(int(year), int(month), int(day))
        date = hdate.HDate(gregorian_date, hebrew=False)
        await create_embed(ctx, date.hebrew_date)


def setup(bot):
    bot.add_cog(HebrewDate(bot))
