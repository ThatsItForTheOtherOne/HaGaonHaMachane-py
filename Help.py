import discord
from discord.ext import commands
from aiohttp import ClientSession
from sendText import createEmbed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
    
    @commands.command(name="help")
    async def helpCommand(self, ctx):
        prefix = self.bot.command_prefix
        await createEmbed(ctx, 'Commands:\n' + prefix +'text\nGrabs Jewish Holy Texts from Sefaria\n' + prefix + 'dailyOverview\nPrints today\'s events on the Jewish calendar\n' + '[Find me on Github!](https://github.com/Acher224/HaGaon-py)')

def setup(bot):
    bot.add_cog(Help(bot))