import discord
from discord.ext import commands
from aiohttp import ClientSession
from SendText import create_embed


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="help")
    async def help_command(self, ctx, *, command: str = "help"):
        command = command.lower()

        if command == "help":
            embed = discord.Embed(
                title="Help",
                color=0x0000FF,
                description="**Type " + self.bot.command_prefix + "help <category>**, e.g. `!!help text`",
            )
            embed.add_field(name="Sections", value="\n• Text\n• Calendar\n", inline=False)
            embed.add_field(
                name="Help",
                value="• Code: https://github.com/Acher224/HaGaonHaMachane-py\n •Invite: TEMPORARILY REMOVED (DM for reason)",
                inline=False,
            )
            embed.set_footer(
                text=self.bot.description,
                icon_url="https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024",
            )
            await ctx.send(embed=embed)

        elif command == "text":
            embed = discord.Embed(title="Get Text", colour=0x0000FF)
            embed.add_field(
                name="text",
                inline=True,
                value="Grabs text from Sefaria API."
                "\n\n__Usage__"
                "\n\n`!!text <work> <chapter>:<verse>`"
                "\n\nExample: `!!text Genesis 1:1`"
                "\n\n`!!text <work> <chapter>:<first verse>-<last verse>`"
                "\n\nExample: `!!text II Kings 2:1-7`",
            )
            embed.add_field(
                name="hebrewText",
                inline=True,
                value="Grabs text from Sefaria API and posts it in Hebrew."
                "\n\n__Usage__"
                "\n\n`!!hebrewText <work> <chapter>:<verse>`"
                "\n\nExample: `!!hebrewText Genesis 1:1`"
                "\n\n`!!hebrewText <work> <chapter>:<first verse>-<last verse>`"
                "\n\nExample: `!!hebrewText II Kings 2:1-7`",
            )

            embed.set_footer(
                text=self.bot.description,
                icon_url="https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024",
            )
            await ctx.send(embed=embed)

        elif command == "calendar":
            embed = discord.Embed(title="Calendar commands", colour=0x0000FF)
            embed.add_field(
                name="hebrewDate",
                inline=True,
                value="Converts today's date to the Hebrew date"
                "\n\n__Usage__"
                "\n\nExample: `!!hebrewDate`",
            )
            embed.add_field(
                name="eventsToday",
                inline=True,
                value="Prints daily event, including Omer count and holidays"
                "\n\n__Usage__"
                "\n\nExample: `!!eventsToday`",
            )
            embed.add_field(
                name="dateToHebrew",
                inline=True,
                value="Converts a date to the date on the Hebrew calendar"
                "\n\n__Usage__"
                "\n\n``!!dateToHebrew <year> <month> <day>``"
                "\n\nExample: `!!dateToHebrew 2020 1 1`",
            )
            embed.add_field(
                name="setLocation",
                inline=True,
                value="Sets a location for zmanim.\n Latitude and Longitude assume N and E.\n timezones must follow tzdata [https://en.wikipedia.org/wiki/List_of_tz_database_time_zones] standards."
                "\n\n__Usage__"
                "\n\n``!!setLocation <Latitude> <Longitude> <tzdata timezone> <diaspora true/false>``"
                "\n\nExample: `!!setLocation 40.7128 -74.0060 America/New_York True`",
            )
            embed.add_field(
                name="Zmanim",
                inline=True,
                value="Prints Zmanim (You must run setLocation first!!!)"
                "\n\n__Usage__"
                "\n\n``!!zmanim``"
                "\n\nExample: `!!zmanim`",
            )

            embed.set_footer(
                text=self.bot.description,
                icon_url="https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024",
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
