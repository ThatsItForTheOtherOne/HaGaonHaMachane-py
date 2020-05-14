import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import datetime
import json
from urllib.request import urlopen


class Status(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = 'https://www.hebcal.com/converter/?cfg=json'
        self.changeStatus.start()

    async def currentHebrewDate(self):
        date = datetime.datetime.now()
        api_url = ''.join((self.api_url,
                           "&gy=",
                            date.strftime('%Y'),
                            "&gm=",
                            date.strftime('%m'),
                            "&gd=",
                            date.strftime('%d')))
        date_obj = json.load(urlopen(api_url))
        dateStr = str(date_obj['hd']) + " " + date_obj['hm'] + ", " + str(date_obj['hy'])
        return dateStr

    async def currentParshaAndHoliday(self):
        date = datetime.datetime.now()
        api_url = ''.join((self.api_url,
                           "&gy=",
                            date.strftime('%Y'),
                            "&gm=",
                            date.strftime('%m'),
                            "&gd=",
                            date.strftime('%d')))
        date_obj = json.load(urlopen(api_url))
        eventStr = ", ".join(date_obj['events'])
        return eventStr

    @tasks.loop(hours=1)
    async def changeStatus(self):
        game = discord.Game(''.join((self.bot.command_prefix,
                                     'help | The date is ',
                                     await self.currentHebrewDate(),
                                    ' | Today\'s events: ',
                                    await self.currentParshaAndHoliday())))
        await self.bot.change_presence(status=discord.Status.idle, activity=game)

def setup(bot):
    bot.add_cog(Status(bot))
