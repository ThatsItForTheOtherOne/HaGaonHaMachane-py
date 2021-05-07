import aiohttp
import discord
from discord.ext import commands
import json
from urllib.request import urlopen
from sendText import create_embed
from aiohttp import ClientSession
import aiosqlite
import re
from typing import List, Tuple

class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/texts/"
    
    async def parse_sefaria_text(self, sefaria_text):
        if not "<i></i>" in sefaria_text and "<i>" in sefaria_text and "</i>" in sefaria_text:
            sefaria_text = sefaria_text.replace("<i>", "*")
            sefaria_text = sefaria_text.replace("</i>", "*")
        else:
            sefaria_text = sefaria_text.replace("<i>", "")
            sefaria_text = sefaria_text.replace("</i>", "")
        if "<b>" in sefaria_text and "</b>" in sefaria_text:
            sefaria_text = sefaria_text.replace("<b>", "**")
            sefaria_text = sefaria_text.replace("</b>", "**")
        else:
            sefaria_text = sefaria_text.replace("<b>", "")
            sefaria_text = sefaria_text.replace("</b>", "")
        if "<strong>" in sefaria_text and "</strong>" in sefaria_text:
            sefaria_text = sefaria_text.replace("<strong>", "***")
            sefaria_text = sefaria_text.replace("</strong>", "***")
        else:
            sefaria_text = sefaria_text.replace("<strong>", "")
            sefaria_text = sefaria_text.replace("</strong>", "")
        sefaria_text = sefaria_text.replace("<span class=\"font1\">", "")
        sefaria_text = sefaria_text.replace("</span>", "")
        sefaria_text = sefaria_text.replace("<br>", "\n")
        sefaria_text = sefaria_text.replace("&lt;", "")
        sefaria_text = sefaria_text.replace("&gt;", "")
        return sefaria_text

    async def text_command(self, ctx, *verse):
        if ctx.command.name == "hebrewText":
            key_type = "he"
        elif ctx.command.name == "text":
            key_type = "text"
        async def parse_verse(verse: str) -> str:
            async def parse_verses(verse: str) -> Tuple[str, str]:
                if "-" in verse:
                    book, chapter, first, final = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()
                    return (f"{book}.{chapter}.{first}-{final}", book)

                elif ":" in verse:
                    book, chapter, verse = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
                    return (f"{book}.{chapter}.{verse}", book)

                else:
                    book, verse = re.compile(r"(\S+)\s(\S+)", re.IGNORECASE).match(verse).groups()
                    return (f"{book}.{verse}", book)

            url, book = await parse_verses(verse)
            return f"{self.api_url}{url}?context=0{await self.get_translation(ctx, book)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(await parse_verse(await self.replace_spaces_with_underscores(" ".join(verse)))) as response:
                body = await response.text()

                if response.status == 404:
                    await create_embed(ctx, "This verse doesn't exist. Check that your input is well formed, or that the verse is available in your desired translation.")
                    return

                sefaria_obj = json.loads(body)

        if isinstance(verses := sefaria_obj[key_type], list):
            verse_text = " ".join(verses)
        elif isinstance(verse := sefaria_obj[key_type], str):
            verse_text = verse
        else:
            typeof = type(sefaria_obj[key_type]).__name__
            await create_embed(ctx, f"The Sefaria API returned something that I don't understand ({typeof}). Please contact my administrator about this error.")
            return

        await create_embed(ctx, await self.parse_sefaria_text(verse_text))
        
    async def replace_spaces_with_underscores(self, string):
        while string.count(" ") != 0 and string.count(" ") != 1:
            string = re.sub(" ", "_", string, count=1)
        return string

    async def get_translation(self, ctx, book):
        db = await aiosqlite.connect("haGaon.db")
        book = book.replace("_", " ")
        cursor = await db.cursor()
        await cursor.execute(
            """SELECT translation FROM translation WHERE work = ? AND user_id = ?""",
            (book, ctx.message.author.id),
        )
        result = await cursor.fetchone()
        if result is None or result[0] is None or result[0] == "":
            await cursor.execute("""SELECT translation FROM default_translation WHERE work = ?""", (book,))
            result = await cursor.fetchone()
        if result is None or result[0] is None or result[0] == "":
            return "&ven="
        translation = result[0].replace(" ", "_")
        await cursor.close()
        await db.close()
        return f"&ven={translation}"

    async def set_translation(self, ctx, *string):
        string = " ".join(string)
        try:
            parsed_string = re.compile(r"(\'.*?\')\s(\'.*?\')").match(string).groups()
        except:
            await create_embed(ctx, f"Invalid parameters! Check {self.bot.command_prefix}help for usage!")
            return
        book = parsed_string[0].replace("'", "")
        translation = parsed_string[1].replace("'", "")
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        sql = "SELECT user_id FROM main WHERE user_id = ?"
        val = (ctx.message.author.id,)
        await cursor.execute(sql, val)
        result = await cursor.fetchone()
        if result is None:
            sql = "INSERT INTO translation(user_id, work, translation) VALUES(?, ?, ?)"
            val = (ctx.message.author.id, book, translation)
        elif result is not None:
            sql = "UPDATE translation SET work = ?, translation = ? WHERE user_id = ?"
            val = (book, translation, ctx.message.author.id)
        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()
        if translation == "":
            await create_embed(ctx, f"Translation for {book} set to default successfully!")
        else:
            await create_embed(ctx, f"Translation for {book} set to {translation} successfully!")

    @commands.command(name="hebrewText")
    async def hebrew_text_command(self, ctx, *verse):
        await self.text_command(ctx, *verse)

    @commands.command(name="text")
    async def regular_text_command(self, ctx, *verse):
        await self.text_command(ctx, *verse)

    @commands.command(name="setTranslation")
    async def set_translation_command(self, ctx, *string):
        await self.set_translation(ctx, *string)




def setup(bot):
    bot.add_cog(Text(bot))