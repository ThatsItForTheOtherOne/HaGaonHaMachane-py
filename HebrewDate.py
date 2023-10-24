import discord
from discord.ext import tasks
import aiohttp
from sendText import create_embed
import datetime
import hdate
import json


class HebrewDate(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
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
    @discord.app_commands.command(name="hebrew_date", description="Get today's hebrew date")
    @discord.app_commands.guild_only
    async def hebrew_date_command(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        await create_embed(ctx, date.hebrew_date)
    
    @discord.app_commands.command(name="events", description="See today's daily readings")
    @discord.app_commands.guild_only
    async def events_today_command(self, ctx):
        await create_embed(ctx, self.events_str)

    @discord.app_commands.command(name="date_to_hebrew", description="Convert a Gregorian date to hebrew")
    @discord.app_commands.guild_only
    async def date_to_hebrew_command(self, ctx, year: int, month: int, day: int):
        gregorian_date = datetime.datetime(year, month, day)
        date = hdate.HDate(gregorian_date, hebrew=False)
        await create_embed(ctx, date.hebrew_date)


async def setup(bot):
    await bot.add_cog(HebrewDate(bot))
