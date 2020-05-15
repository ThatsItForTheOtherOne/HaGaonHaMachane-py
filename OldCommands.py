import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
from sendText import createEmbed


async def sendDepcrecatedMessage(self, ctx):
    await createEmbed(
        ctx,
        "These Commands are now deprecated. Use "
        + self.bot.command_prefix
        + "text. You no longer need to specify what work, only the citation.",
    )


class OldCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="tanakh")
    async def tanakh(self, ctx):
        await sendDepcrecatedMessage(self, ctx)

    @commands.command(name="mishnah")
    async def mishnah(self, ctx):
        await sendDepcrecatedMessage(self, ctx)

    @commands.command(name="talmud")
    async def talmud(self, ctx):
        await sendDepcrecatedMessage(self, ctx)


def setup(bot):
    bot.add_cog(OldCommands(bot))
