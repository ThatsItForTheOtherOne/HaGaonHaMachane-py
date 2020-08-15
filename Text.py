import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import re
from SendText import create_embed
from aiohttp import ClientSession
from markdownify import markdownify as md
import sqlite3


class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/texts/"

    def get_translation(self, ctx, book):
        if book in [
            "Genesis",
            "Exodus",
            "Leviticus",
            "Numbers",
            "Deteronomy",
            "Amos",
            "Ezekiel",
            "Habakkuk",
            "Haggai",
            "Hosea",
            "I_Kings",
            "I_Samuel",
            "II_Kings",
            "II_Samuel",
            "Isaiah",
            "Jeremiah",
            "Joel",
            "Jonah",
            "Joshua",
            "Judges",
            "Malachi",
            "Micah",
            "Nahum",
            "Obadiah",
            "Zechariah",
            "Zephaniah",
            "Daniel",
            "Ecclesiastes",
            "Esther",
            "Ezra",
            "I_Chronicles",
            "II_Chronicles",
            "Job",
            "Lamentations",
            "Nehemiah",
            "Proverbs",
            "Psalms",
            "Ruth",
            "Song of Songs",
        ]:
            return "&ven=The_Koren_Jerusalem_Bible"
        else:
            return ""

    @commands.command(name="text")
    async def text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = re.sub(r"[^\S\r\n](?=[A-z])", "_", verse)
        if "-" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()

            book = parsed_string[0]
            chapter = int(parsed_string[1])
            first_verse = int(parsed_string[2]) - 1
            final_verse = int(parsed_string[3])

            api_url = f"{self.api_url}{book}.{chapter}.{first_verse}?{self.get_translation(ctx, book)}"
            sefaria_obj = json.load(urlopen(api_url))
            verses_list = sefaria_obj["text"][first_verse:final_verse]
            verse_text = " ".join(verses_list)
            await create_embed(ctx, md(verse_text))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()

            book = parsed_string[0]
            chapter = int(parsed_string[1])
            verse = int(parsed_string[2])

            api_url = f"{self.api_url}{book}.{chapter}.{verse}?context=0{self.get_translation(ctx, book)}"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["text"]))

    @commands.command(name="hebrewText")
    async def hebrew_text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = re.sub(r"[^\S\r\n](?=[A-z])", "_", verse)
        if "-" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()

            book = parsed_string[0]
            chapter = int(parsed_string[1])
            first_verse = int(parsed_string[2]) - 1
            final_verse = int(parsed_string[3])

            api_url = f"{self.api_url}{book}.{chapter}.{first_verse}"
            sefaria_obj = json.load(urlopen(api_url))
            verses_list = sefaria_obj["he"][first_verse:final_verse]
            verse_text = " ".join(verses_list)
            await create_embed(ctx, md(verse_text))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()

            book = parsed_string[0]
            chapter = int(parsed_string[1])
            verse = int(parsed_string[2])

            api_url = f"{self.api_url}{book}.{chapter}.{verse}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["he"]))


def setup(bot):
    bot.add_cog(Text(bot))
