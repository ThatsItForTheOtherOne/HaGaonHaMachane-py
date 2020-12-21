import discord
from discord.ext import commands, tasks
from aiohttp import ClientSession
import aiosqlite
from sendText import create_embed
import hdate
import datetime
from geopy.geocoders import Nominatim
from tzwhere import tzwhere


class Zmanim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)

    @commands.command(name="setLocationByCoordinates")
    async def set_location_by_coordinates(self, ctx, latitude, longtiude, timezone, diaspora):
        if ctx.channel.type is not discord.ChannelType.private:
            await create_embed(ctx, "This command is only for DMs!")
        else:
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            await cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.message.author.id}")
            result = await cursor.fetchone()
            if result is None:
                sql = (
                    "INSERT INTO main(user_id, latitude, longitude, timezone, diaspora) VALUES(?, ?, ?, ?, ?)"
                )
                val = (ctx.message.author.id, latitude, longtiude, timezone, diaspora)
            elif result is not None:
                sql = "UPDATE main SET latitude = ?, longitude  = ?, timezone = ?, diaspora = ? WHERE user_id = ?"
                val = (latitude, longtiude, timezone, diaspora, ctx.message.author.id)
            await cursor.execute(sql, val)
            await db.commit()
            await cursor.close()
            await db.close()
            await create_embed(ctx, "Location Set and Saved!")

    @commands.command(name="setLocationByAddress")
    async def set_location_by_address(self, ctx, *address):
        if ctx.channel.type is not discord.ChannelType.private:
            await create_embed(ctx, "This command is only for DMs!")
        else:
            geolocator = Nominatim(user_agent="HaGaon HaMachane")
            address_str = " ".join(address)
            location = geolocator.geocode(address_str, language="en")
            await create_embed(ctx, "Processing, this will take a second...")
            tzwhere_obj = tzwhere.tzwhere()
            timezone = tzwhere_obj.tzNameAt(location.latitude, location.longitude)
            if "Israel" in location.address:
                diaspora = "True"
            else:
                diaspora = "False"
            print(f"{timezone} {diaspora} {location.raw}")
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            await cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.message.author.id}")
            result = await cursor.fetchone()
            if result is None:
                sql = (
                    "INSERT INTO main(user_id, latitude, longitude, timezone, diaspora) VALUES(?, ?, ?, ?, ?)"
                )
                val = (ctx.message.author.id, location.latitude, location.longitude, timezone, diaspora)
            elif result is not None:
                sql = "UPDATE main SET latitude = ?, longitude  = ?, timezone = ?, diaspora = ? WHERE user_id = ?"
                val = (location.latitude, location.longitude, timezone, diaspora, ctx.message.author.id)
            await cursor.execute(sql, val)
            await db.commit()
            await cursor.close()
            await db.close()
            await create_embed(ctx, "Location Set and Saved!")

    @commands.command(name="zmanim")
    async def getZmanim(self, ctx):
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * FROM main WHERE user_id = {ctx.message.author.id}")
        result = await cursor.fetchone()
        if result is None:
            await create_embed(ctx, "Run setLocation first!!")
        elif result is not None:
            dias = result[4] == "True"
            location = hdate.Location(
                longitude=float(result[2]), latitude=float(result[1]), timezone=result[3], diaspora=dias,
            )
            await create_embed(ctx, str(hdate.Zmanim(location=location, hebrew=False)))
        await cursor.close()
        await db.close()


def setup(bot):
    bot.add_cog(Zmanim(bot))
