import discord
from discord.ext import commands
from aiohttp import ClientSession
from sendText import createEmbed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
    
    @commands.command(name="help")
    async def helpCommand(self, ctx, *, command: str = 'help'):
        command = command.lower()

        if command == 'help':
            embed = discord.Embed(title = 'Help', color = 0x0000ff, description="**Type " + self.bot.command_prefix + "help <category>**, e.g. `!!help text`")
            embed.add_field(name="Sections", value='\n• Text\n• Calendar\n', inline=False)
            embed.add_field(name="Help", value="• Code: https://github.com/Acher224/HaGaonHaMachane-py\n •Invite: https://discord.com/oauth2/authorize?client_id=466676353907818516&scope=bot&permissions=68608", inline=False)
            embed.set_footer(text=self.bot.description,icon_url='https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024')
            await ctx.send(embed=embed)

        elif command == 'text':
            embed = discord.Embed(title="Get Text", colour=0x0000ff)
            embed.add_field(name="text", inline=True, value="Grabs text from Sefaria API."
                                              "\n\n__Usage__"
                                              "\n\n`!!text <work> <chapter>:<verse>`"
                                              "\n\nExample: `!!text Genesis 1:1`"
                                              "\n\n`!!text <work> <chapter>:<first verse>-<last verse>`"
                                              "\n\nExample: `!!text II Kings 2:1-7`")
            embed.set_footer(text=self.bot.description,icon_url='https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024')
            await ctx.send(embed=embed)

        elif command == 'calendar':
            embed = discord.Embed(title="Calendar commands", colour=0x0000ff)
            embed.add_field(name="hebrewDate", inline=True, value="Converts today\'s date to the Hebrew date"
                                              "\n\n__Usage__"
                                              "\n\nExample: `!!hebrewDate`")
            embed.add_field(name="dailyOverview", inline=True, value="Converts today\'s date to the Hebrew date and grabs daily events"
                                              "\n\n__Usage__"
                                              "\n\nExample: `!!dailyOverview`")
            embed.set_footer(text=self.bot.description,icon_url='https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024')
            await ctx.send(embed=embed)
            





def setup(bot):
    bot.add_cog(Help(bot))