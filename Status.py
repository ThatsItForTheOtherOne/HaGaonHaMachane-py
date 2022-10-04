import discord
import aiohttp
import datetime
import hdate
import json
from urllib.request import urlopen


class Status(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/calendars"
        self.change_status.start()

    @discord.ext.tasks.loop(hours=1)
    async def change_status(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                body = await response.text()
                sefaria_obj = json.loads(body)
            date = hdate.HDate(datetime.datetime.now(), hebrew=False)
            status_string = f"""
                    {self.bot.description}
                    | {date.hebrew_date}
                    | Today's Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    | Today's Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    """
            status_string = status_string.replace("\n", " ")
            status_string = status_string.replace("\r", " ")
            status_string = status_string.replace("                    ", "")
            if len(status_string) > 128:
                status_string = f"""
                    {date.hebrew_date}
                    | Today's Parasha: {sefaria_obj["calendar_items"][0]["displayValue"]["en"]}
                    | Today's Haftarah: {sefaria_obj["calendar_items"][1]["displayValue"]["en"]}
                    """
                status_string = status_string.replace("\n", " ")
                status_string = status_string.replace("\r", " ")
                status_string = status_string.replace("                    ", "")
            print(f"The status string is {len(status_string)} chars")
            game = discord.Game(status_string)
            await self.bot.change_presence(status=discord.Status.online, activity=game)


async def setup(bot):
    await bot.add_cog(Status(bot))
