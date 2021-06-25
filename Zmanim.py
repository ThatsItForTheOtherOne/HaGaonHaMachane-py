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

    async def set_location_by_coordinates(self, ctx, latitude, longtiude, timezone, diaspora):
        if ctx.channel.type is not discord.ChannelType.private:
            await create_embed(ctx, "This command is only for DMs!")
        else:
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            sql = "SELECT user_id FROM main WHERE user_id = ?"
            val = (ctx.message.author.id,)
            await cursor.execute(sql, val)
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
                diaspora = "False"
            else:
                diaspora = "True"
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            sql = "SELECT user_id FROM main WHERE user_id = ?"
            val = (ctx.message.author.id,)
            await cursor.execute(sql, val)
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

    async def get_zmanim(self, ctx):
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        sql = "SELECT * FROM main WHERE user_id = ?"
        val = (ctx.message.author.id,)
        await cursor.execute(sql, val)
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

    @commands.command(
        name="setLocationByCoordinates", aliases=["set_location_by_coordinates", "setlocationbycoordinates"]
    )
    async def set_loc_by_coords_command(self, ctx, latitude, longtiude, timezone, diaspora):
        await self.set_location_by_coordinates(ctx, latitude, longtiude, timezone, diaspora)

    @commands.command(
        name="setLocationByAddress", aliases=["set_location_by_address", "setlocationbyaddress"]
    )
    async def set_loc_by_address_command(self, ctx, *address):
        await self.set_location_by_address(ctx, *address)

    @commands.command(name="zmanim")
    async def get_zmanim_command(self, ctx):
        await self.get_zmanim(ctx)


def setup(bot):
    bot.add_cog(Zmanim(bot))
