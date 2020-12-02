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
        if "<i>" in sefaria_text and "</i>" in sefaria_text:
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
        sefaria_text = sefaria_text.replace("<br>", "\n")
        return sefaria_text
        
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

    @commands.command(name="setTranslation")
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
        await cursor.execute(f"SELECT user_id FROM translation WHERE user_id = {ctx.message.author.id}")
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

    @commands.command(name="text")
    async def text_command(self, ctx, *verse):
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

        if isinstance(verses := sefaria_obj["text"], list):
            verse_text = " ".join(verses)
        elif isinstance(verse := sefaria_obj["text"], str):
            verse_text = verse
        else:
            typeof = type(sefaria_obj["text"]).__name__
            await create_embed(ctx, f"The Sefaria API returned something that I don't understand ({typeof}). Please contact my administrator about this error.")
            return

        await create_embed(ctx, await self.parse_sefaria_text(verse_text))

    @commands.command(name="hebrewText")
    async def hebrew_text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = await self.replace_spaces_with_underscores(verse)
        if "-" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            chapter = parsed_string[1]
            first_verse = int(parsed_string[2])
            final_verse = int(parsed_string[3])

            api_url = f"{self.api_url}{book}.{chapter}.{first_verse}"
            sefaria_obj = json.load(urlopen(api_url))
            verses_list = sefaria_obj["he"][first_verse - 1 : final_verse]
            verse_text = " ".join(verses_list)
            await create_embed(ctx, self.parse_sefaria_text(verse_text))
        elif ":" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            chapter = parsed_string[1]
            verse = int(parsed_string[2])

            api_url = f"{self.api_url}{book}.{chapter}.{verse}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, self.parse_sefaria_text(sefaria_obj["he"]))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            verse = int(parsed_string[1])

            api_url = f"{self.api_url}{book}.{verse}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, self.parse_sefaria_text(sefaria_obj["he"]))


def setup(bot):
    bot.add_cog(Text(bot))