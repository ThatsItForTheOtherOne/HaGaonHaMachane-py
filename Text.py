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
            api_url = f"{self.api_url}{parsed_string[0]}.{parsed_string[1]}.{parsed_string[2]}?{self.get_translation(ctx, parsed_string[0])}"
            sefaria_obj = json.load(urlopen(api_url))
            verse_text = ""
            for x in range(int(parsed_string[2]) - 1, int(parsed_string[3])):
                verse_text = verse_text + " " + sefaria_obj["text"][x]
            await create_embed(ctx, md(verse_text))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
            api_url = f"{self.api_url}{parsed_string[0]}.{parsed_string[1]}.{parsed_string[2]}?context=0{self.get_translation(ctx, parsed_string[0])}"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["text"]))

    @commands.command(name="hebrewText")
    async def hebrew_text_command(self, ctx, *verse):
        verse = " ".join(verse)
        verse = re.sub(r"[^\S\r\n](?=[A-z])", "_", verse)
        if "-" in verse:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE).match(verse).groups()
            api_url = f"{self.api_url}{parsed_string[0]}.{parsed_string[1]}.{parsed_string[2]}"
            sefaria_obj = json.load(urlopen(api_url))
            verse_text = ""
            for x in range(int(parsed_string[2]) - 1, int(parsed_string[3])):
                verse_text = verse_text + " " + sefaria_obj["he"][x]
            await create_embed(ctx, md(verse_text))
        else:
            parsed_string = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE).match(verse).groups()
            api_url = f"{self.api_url}{parsed_string[0]}.{parsed_string[1]}.{parsed_string[2]}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await create_embed(ctx, md(sefaria_obj["he"]))


def setup(bot):
    bot.add_cog(Text(bot))
