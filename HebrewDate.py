import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
from sendText import createEmbed
import datetime
import hdate

class HebrewDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="hebrewDate")
    async def hebrewDate(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        await createEmbed(ctx, date.hebrew_date)

    @commands.command(name="eventsToday")
    async def eventsToday(self, ctx):
        date = hdate.HDate(datetime.datetime.now(), hebrew=False)
        if date.is_holiday == False and 0 < date.omer_day < 50:
            eventStr = ''.join(('The parasha is ', date.parasha, 
                                ' and it is ', str(date.omer_day), ' days in the omer.'
                                ' The daf yomi is ', date.daf_yomi, '.'))
        elif date.is_holiday == False:
            eventStr = ''.join(('The parasha is ', date.parasha, 
                                ' and today is not a holiday.'
                                ' The daf yomi is ', date.daf_yomi, '.'))
        else:
            eventStr = ''.join(('The parasha is  ', date.parasha, 
                                ' and today is ', date.holiday_name, '.'
                                ' The daf yomi is ', date.daf_yomi, '.'))

        await createEmbed(ctx, eventStr)
    
    @commands.command(name="dateToHebrew")
    async def dateToHebrew(self, ctx, year, month, day):
        gregorianDate = datetime.datetime(int(year), int(month), int(day))
        date = hdate.HDate(gregorianDate, hebrew=False)
        await createEmbed(ctx, date.hebrew_date)
    






def setup(bot):
    bot.add_cog(HebrewDate(bot))
