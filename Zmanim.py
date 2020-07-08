import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import sqlite3
from sendText import createEmbed
import hdate
import datetime


class Zmanim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="setLocation")
    async def setLocation(self, ctx, latitude, longtiude, timezone, diaspora):
        db = sqlite3.connect("haGaon.db")
        cursor = db.cursor()
        cursor.execute(
            f"SELECT user_id FROM main WHERE user_id = {ctx.message.author.id}"
        )
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO main(user_id, latitude, longitude, timezone, diaspora) VALUES(?, ?, ?, ?, ?)"
            val = (ctx.message.author.id, latitude, longtiude, timezone, diaspora)
        elif result is not None:
            sql = "UPDATE main SET latitude = ?, longitude  = ?, timezone = ?, diaspora = ? WHERE user_id = ?"
            val = (latitude, longtiude, timezone, diaspora, ctx.message.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await createEmbed(ctx, "Location Set and Saved!")

    @commands.command(name="zmanim")
    async def getZmanim(self, ctx):
        db = sqlite3.connect("haGaon.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM main WHERE user_id = {ctx.message.author.id}")
        result = cursor.fetchone()
        dias = result[4].lower() == "true"
        location = hdate.Location(
            longitude=float(result[2]),
            latitude=float(result[1]),
            timezone=result[3],
            diaspora=dias,
        )
        await createEmbed(ctx, str(hdate.Zmanim(location=location, hebrew=False)))


def setup(bot):
    bot.add_cog(Zmanim(bot))
