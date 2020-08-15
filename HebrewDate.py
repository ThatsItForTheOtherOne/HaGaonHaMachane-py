import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
from SendText import create_embed
import datetime
import hdate
import json
from urllib.request import urlopen


class HebrewDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/calendars"

    @commands.command(name="hebrewDate")
    async def hebrew_date(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        await create_embed(ctx, date.hebrew_date)

    @commands.command(name="eventsToday")
    async def events_today(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        sefaria_obj = json.load(urlopen(self.api_url))
        if date.is_holiday == False and 0 < date.omer_day < 50:
            event_string = f"""
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
            event_string = f"""
                    Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    Daf Yomi: {sefaria_obj["calendar_items"][2]["displayValue"]["en"]}
                    Mishnah Yomit: {sefaria_obj["calendar_items"][4]["displayValue"]["en"]}
                    Daily Rambam 1 Chapter: {sefaria_obj["calendar_items"][5]["displayValue"]["en"]}
                    Daily Rambam 3 Chapters: {sefaria_obj["calendar_items"][6]["displayValue"]["en"]}
                    Halakha Yomit: {sefaria_obj["calendar_items"][8]["displayValue"]["en"]}
                    """
        else:
            event_string = f"""
                    Holiday: {date.holiday_description}
                    Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    Daf Yomi: {sefaria_obj["calendar_items"][2]["displayValue"]["en"]}
                    Mishnah Yomit: {sefaria_obj["calendar_items"][4]["displayValue"]["en"]}
                    Daily Rambam 1 Chapter: {sefaria_obj["calendar_items"][5]["displayValue"]["en"]}
                    Daily Rambam 3 Chapters: {sefaria_obj["calendar_items"][6]["displayValue"]["en"]}
                    Halakha Yomit: {sefaria_obj["calendar_items"][8]["displayValue"]["en"]}
                    """
        await create_embed(ctx, event_string)

    @commands.command(name="dateToHebrew")
    async def date_to_hebrew(self, ctx, year, month, day):
        gregorian_date = datetime.datetime(int(year), int(month), int(day))
        date = hdate.HDate(gregorian_date, hebrew=False)
        await create_embed(ctx, date.hebrew_date)


def setup(bot):
    bot.add_cog(HebrewDate(bot))
