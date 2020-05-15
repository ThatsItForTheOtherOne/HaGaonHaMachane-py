import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import datetime
import json
from urllib.request import urlopen
import hdate

class Status(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = 'https://www.hebcal.com/converter/?cfg=json'
        self.changeStatus.start()

    async def currentHebrewDate(self):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        return date.hebrew_date

    async def currentParasha(self):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        parashaStr = ' '.join(('Parashat', date.parasha))
        return parashaStr

    @tasks.loop(hours=1)
    async def changeStatus(self):
        game = discord.Game(''.join((self.bot.command_prefix,
                                'help | The date is ',
                                await self.currentHebrewDate(),
                                ' | Today\'s parasha: ',
                                await self.currentParasha())))
        await self.bot.change_presence(status=discord.Status.online, activity=game)

def setup(bot):
    bot.add_cog(Status(bot))
