import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import json
from urllib.request import urlopen
from sendText import createEmbed
import datetime


class HebrewDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = 'https://www.hebcal.com/converter/?cfg=json'
        self.changeStatus.start()


    async def currentHebrewDate(self):
        date = datetime.datetime.now()
        date_obj = json.load(urlopen(self.api_url + "&gy=" + date.strftime('%Y') + "&gm=" + date.strftime('%m') + "&gd=" + date.strftime('%d')))
        dateStr = str(date_obj['hd']) + " " + date_obj['hm'] + ", " + str(date_obj['hy'])
        return dateStr
    async def currentParshaAndHoliday(self):
        date = datetime.datetime.now()
        date_obj = json.load(urlopen(self.api_url + "&gy=" + date.strftime('%Y') + "&gm=" + date.strftime('%m') + "&gd=" + date.strftime('%d')))
        eventStr = ", ".join(date_obj['events'])
        return eventStr
        
    @commands.command(name="hebrewDate")
    async def hebrewDate(self, ctx):
        await createEmbed(ctx, await self.currentHebrewDate())

    @commands.command(name="eventsToday")
    async def eventsToday(self, ctx):
        await createEmbed(ctx, await self.currentParshaAndHoliday())
    
    @commands.command(name="dailyOverview")
    async def dailyOverview(self, ctx):
        overviewStr = 'Today\'s date is' + await self.currentHebrewDate() + ' the daily parsha and holidays today are: ' + await self.currentParshaAndHoliday()
        await createEmbed(ctx, overviewStr)

    @tasks.loop(hours=1)
    async def changeStatus(self):
        game = discord.Game(self.bot.command_prefix + 'help | HaGaon 1.0! | The date is ' + await self.currentHebrewDate() + ' | Today\'s events: ' + await self.currentParshaAndHoliday())
        await self.bot.change_presence(status=discord.Status.idle, activity=game)




def setup(bot):
    bot.add_cog(HebrewDate(bot))
