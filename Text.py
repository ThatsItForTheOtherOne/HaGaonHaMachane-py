import discord
from discord.ext import commands
import json
from urllib.request import urlopen
from SendText import create_embed
from aiohttp import ClientSession
from markdownify import markdownify as md
import sqlite3
import re


class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/texts/"

    def replace_spaces_with_underscores(self, string):
        while string.count(" ") != 0 and string.count(" ") != 1:
            string = re.sub(" ", "_", string, count=1)
        return string

    def get_translation(self, ctx, book):
        db = sqlite3.connect("haGaon.db")
        book = book.replace("_", " ")
        cursor = db.cursor()
        cursor.execute(
            """SELECT translation FROM translation WHERE work = ? AND user_id = ?""",
            (book, ctx.message.author.id),
        )
        result = cursor.fetchone()
        if result is None or result[0] is None or result[0] == "":
            cursor.execute("""SELECT translation FROM default_translation WHERE work = ?""", (book,))
            result = cursor.fetchone()
        if result is None or result[0] is None or result[0] == "":
            return "&ven="
        translation = result[0].replace(" ", "_")
        cursor.close()
        db.close()
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
        db = sqlite3.connect("haGaon.db")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM translation WHERE user_id = {ctx.message.author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = "INSERT INTO translation(user_id, work, translation) VALUES(?, ?, ?)"
            val = (ctx.message.author.id, book, translation)
        elif result is not None:
            sql = "UPDATE translation SET work = ?, translation = ? WHERE user_id = ?"
            val = (book, translation, ctx.message.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        if translation == "":
            await create_embed(ctx, f"Translation for {book} set to default successfully!")
        else:
            await create_embed(ctx, f"Translation for {book} set to {translation} successfully!")

    @commands.command(name="text")
    async def text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = self.replace_spaces_with_underscores(verse)
        if "-" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            chapter = parsed_string[1]
            first_verse = int(parsed_string[2])
            final_verse = int(parsed_string[3])

            api_url = f"{self.api_url}{book}.{chapter}.{first_verse}?{self.get_translation(ctx, book)}"
            sefaria_obj = json.load(urlopen(api_url))
            verses_list = sefaria_obj["text"][first_verse - 1 : final_verse]
            verse_text = " ".join(verses_list)
            if verse_text is "":
                await create_embed(
                    ctx, "There is no translation for this verse (or your translation setting is invalid)."
                )
                return
            await create_embed(ctx, md(verse_text))
        elif ":" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            chapter = parsed_string[1]
            verse = int(parsed_string[2])

            api_url = f"{self.api_url}{book}.{chapter}.{verse}?context=0{self.get_translation(ctx, book)}"
            sefaria_obj = json.load(urlopen(api_url))
            if sefaria_obj["text"] is "":
                await create_embed(
                    ctx, "There is no translation for this verse (or your translation setting is invalid)."
                )
                return
            await create_embed(ctx, md(sefaria_obj["text"]))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            verse = int(parsed_string[1])

            api_url = f"{self.api_url}{book}.{verse}?context=0{self.get_translation(ctx, book)}"
            sefaria_obj = json.load(urlopen(api_url))
            if sefaria_obj["text"] is "":
                await create_embed(
                    ctx, "There is no translation for this verse (or your translation setting is invalid)."
                )
                return
            await create_embed(ctx, md(sefaria_obj["text"]))

    @commands.command(name="hebrewText")
    async def hebrew_text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = self.replace_spaces_with_underscores(verse)
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
            await create_embed(ctx, md(verse_text))
        elif ":" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            chapter = parsed_string[1]
            verse = int(parsed_string[2])

            api_url = f"{self.api_url}{book}.{chapter}.{verse}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["he"]))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+)", re.IGNORECASE).match(verse).groups()
            book = parsed_string[0]
            verse = int(parsed_string[1])

            api_url = f"{self.api_url}{book}.{verse}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["he"]))


def setup(bot):
    bot.add_cog(Text(bot))
