import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
from sendText import createEmbed
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
    async def hebrewDate(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        await createEmbed(ctx, date.hebrew_date)

    @commands.command(name="eventsToday")
    async def eventsToday(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        sefaria_obj = json.load(urlopen(self.api_url))
        if date.is_holiday == False and 0 < date.omer_day < 50:
            eventStr = "".join(
                (
                    "Parsha: ",
                    sefaria_obj['calendar_items'][0]['displayValue']['en'],
                    "\nHaftarah: ",
                    sefaria_obj['calendar_items'][1]['displayValue']['en'],
                    "\nOmer count: ",
                    str(date.omer_day),
                    "\nDaf Yomi: ",
                    sefaria_obj['calendar_items'][2]['displayValue']['en'],
                    "\nMishnah Yomit: ",
                    sefaria_obj['calendar_items'][4]['displayValue']['en'],
                    "\nDaily Rambam 1 Chapter: ",
                    sefaria_obj['calendar_items'][5]['displayValue']['en'],
                    "\nDaily Rambam 3 Chapters: ",
                    sefaria_obj['calendar_items'][6]['displayValue']['en'],
                    "\nHalakha Yomit: ",
                    sefaria_obj['calendar_items'][8]['displayValue']['en']
                )
            )
        elif date.is_holiday == False:
            eventStr = "".join(
                (
                    "Parsha: ",
                    sefaria_obj['calendar_items'][0]['displayValue']['en'],
                    "\nHaftarah: ",
                    sefaria_obj['calendar_items'][1]['displayValue']['en'],
                    "\nDaf Yomi: ",
                    sefaria_obj['calendar_items'][2]['displayValue']['en'],
                    "\nMishnah Yomit: ",
                    sefaria_obj['calendar_items'][4]['displayValue']['en'],
                    "\nDaily Rambam 1 Chapter: ",
                    sefaria_obj['calendar_items'][5]['displayValue']['en'],
                    "\nDaily Rambam 3 Chapters: ",
                    sefaria_obj['calendar_items'][6]['displayValue']['en'],
                    "\nHalakha Yomit: ",
                    sefaria_obj['calendar_items'][8]['displayValue']['en']
                )
            )
        else:
            eventStr = "".join(
                (
                    "Holiday: ",
                    date.holiday_name,
                    "Parsha: ",
                    sefaria_obj['calendar_items'][0]['displayValue']['en'],
                    "\nHaftarah: ",
                    sefaria_obj['calendar_items'][1]['displayValue']['en'],
                    "\nDaf Yomi: ",
                    sefaria_obj['calendar_items'][2]['displayValue']['en'],
                    "\nMishnah Yomit: ",
                    sefaria_obj['calendar_items'][4]['displayValue']['en'],
                    "\nDaily Rambam 1 Chapter: ",
                    sefaria_obj['calendar_items'][5]['displayValue']['en'],
                    "\nDaily Rambam 3 Chapters: ",
                    sefaria_obj['calendar_items'][6]['displayValue']['en'],
                    "\nHalakha Yomit: ",
                    sefaria_obj['calendar_items'][8]['displayValue']['en']
                )
            )
        await createEmbed(ctx, eventStr)

    @commands.command(name="dateToHebrew")
    async def dateToHebrew(self, ctx, year, month, day):
        gregorianDate = datetime.datetime(int(year), int(month), int(day))
        date = hdate.HDate(gregorianDate, hebrew=False)
        await createEmbed(ctx, date.hebrew_date)


def setup(bot):
    bot.add_cog(HebrewDate(bot))
