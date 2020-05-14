import discord
from discord.ext import commands


async def createEmbed(ctx, text):
        if (len(text) > 2048): 
            await ctx.send("MESSAGE TOO LONG!")
            return
        embed = discord.Embed(title='HaGaon HaMachane',description=text,color=0x0000ff)
        embed.set_footer(text='HaGaon HaMachane',icon_url='https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024')
        await ctx.send(embed=embed)
