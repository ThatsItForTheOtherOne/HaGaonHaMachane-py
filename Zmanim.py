import discord
import aiohttp
import aiosqlite
from sendText import create_embed
import hdate
from geopy.geocoders import Nominatim
import tzwhere

class Zmanim(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
    
    @discord.app_commands.command(name="set_location_by_coordinates")
    async def set_location_by_coordinates(self, interaction: discord.Interaction, latitude: float, longtiude: float, timezone: str, diaspora: bool):
        if interaction.channel.type is not discord.ChannelType.private:
            await create_embed(interaction, "This command is only for DMs!")
        else:
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            sql = "SELECT user_id FROM main WHERE user_id = ?"
            val = (interaction.user.id,)
            await cursor.execute(sql, val)
            result = await cursor.fetchone()
            if result is None:
                sql = (
                    "INSERT INTO main(user_id, latitude, longitude, timezone, diaspora) VALUES(?, ?, ?, ?, ?)"
                )
                val = (interaction.user.id, latitude, longtiude, timezone, diaspora)
            elif result is not None:
                sql = "UPDATE main SET latitude = ?, longitude  = ?, timezone = ?, diaspora = ? WHERE user_id = ?"
                val = (latitude, longtiude, timezone, diaspora, interaction.user.id)
            await cursor.execute(sql, val)
            await db.commit()
            await cursor.close()
            await db.close()
            await create_embed(interaction, "Location Set and Saved!")
    
    @discord.app_commands.command(name="set_location_by_address")
    async def set_location_by_address(self, interaction: discord.Interaction, address: str):
        if interaction.channel.type is not discord.ChannelType.private:
            await create_embed(interaction, "This command is only for DMs!")
        else:
            geolocator = Nominatim(user_agent="HaGaon HaMachane")
            location = geolocator.geocode(address, language="en")
            await create_embed(interaction, "Processing, this will take a second...")
            tzwhere_obj = tzwhere.tzwhere()
            timezone = tzwhere_obj.tzNameAt(location.latitude, location.longitude)
            if "Israel" in location.address:
                diaspora = "False"
            else:
                diaspora = "True"
            db = await aiosqlite.connect("haGaon.db")
            cursor = await db.cursor()
            sql = "SELECT user_id FROM main WHERE user_id = ?"
            val = (interaction.user.id,)
            await cursor.execute(sql, val)
            result = await cursor.fetchone()
            if result is None:
                sql = (
                    "INSERT INTO main(user_id, latitude, longitude, timezone, diaspora) VALUES(?, ?, ?, ?, ?)"
                )
                val = (interaction.user.id, location.latitude, location.longitude, timezone, diaspora)
            elif result is not None:
                sql = "UPDATE main SET latitude = ?, longitude  = ?, timezone = ?, diaspora = ? WHERE user_id = ?"
                val = (location.latitude, location.longitude, timezone, diaspora, interaction.user.id)
            await cursor.execute(sql, val)
            await db.commit()
            await cursor.close()
            await db.close()
            await create_embed(interaction, "Location Set and Saved!")
    
    @discord.app_commands.command(name="zmanim")
    @discord.app_commands.guild_only
    async def get_zmanim(self, interaction: discord.Interaction):
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        sql = "SELECT * FROM main WHERE user_id = ?"
        val = (interaction.user.id,)
        await cursor.execute(sql, val)
        result = await cursor.fetchone()
        if result is None:
            await create_embed(interaction, "Run setLocation first!!")
        elif result is not None:
            location = hdate.Location(
                longitude=float(result[2]), latitude=float(result[1]), timezone=result[3], diaspora=result[4],
            )
            await create_embed(interaction, str(hdate.Zmanim(location=location, hebrew=False)))
        await cursor.close()
        await db.close()

async def setup(bot):
   await bot.add_cog(Zmanim(bot), guild=discord.Object(id=858012866383970305))
