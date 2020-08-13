import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import re
from sendText import createEmbed
from aiohttp import ClientSession
from markdownify import markdownify as md
import sqlite3




class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/texts/"
    
    def get_translation(self, ctx, book):
        if book in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deteronomy"]:
            return "&ven=The_Koren_Jerusalem_Bible"
        else:
            return ""


    @commands.command(name="text")
    async def textCommand(self, ctx, *verse):
        verse = " ".join(verse)
        verse = re.sub(r"[^\S\r\n](?=[A-z])", "_", verse)
        if "-" in verse:
            exp = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE)
            parsedstring = exp.match(verse).groups()
            api_url = f"{self.api_url}{parsedstring[0]}.{parsedstring[1]}.{parsedstring[2]}?{self.get_translation(ctx, parsedstring[0])}"
            sefaria_obj = json.load(urlopen(api_url))
            versetext = ""
            for x in range(int(parsedstring[2]) - 1, int(parsedstring[3])):
                versetext = versetext + " " + sefaria_obj["text"][x]
            await createEmbed(ctx, md(versetext))
        else:
            exp = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE)
            parsedstring = exp.match(verse).groups()
            api_url = f"{self.api_url}{parsedstring[0]}.{parsedstring[1]}.{parsedstring[2]}?context=0{self.get_translation(ctx, parsedstring[0])}"
            sefaria_obj = json.load(urlopen(api_url))
            await createEmbed(ctx, md(sefaria_obj["text"]))

    @commands.command(name="hebrewText")
    async def hebrewTextCommand(self, ctx, *verse):
        h = html2text.HTML2Text()
        verse = " ".join(verse)
        if verse.count(" ") > 1:
            verse = re.sub(r"[^\S\r\n](?=[A-z])", "_", verse)
        if "-" in verse:
            exp = re.compile(r"(\S+)\s(\S+):(\d+)-(\d+)", re.IGNORECASE)
            parsedstring = exp.match(verse).groups()
            api_url = (
                api_url
            ) = f"{self.api_url}{parsedstring[0]}.{parsedstring[1]}.{parsedstring[2]}"
            sefaria_obj = json.load(urlopen(api_url))
            versetext = ""
            for x in range(int(parsedstring[2]) - 1, int(parsedstring[3])):
                versetext = versetext + " " + sefaria_obj["he"][x]
            await createEmbed(ctx, md(versetext))
        else:
            exp = re.compile(r"(\S+)\s(\S+):(\d+)", re.IGNORECASE)
            parsedstring = exp.match(verse).groups()
            api_url = f"{self.api_url}{parsedstring[0]}.{parsedstring[1]}.{parsedstring[2]}?context=0"
            sefaria_obj = json.load(urlopen(api_url))
            await createEmbed(ctx, md(sefaria_obj["he"]))


def setup(bot):
    bot.add_cog(Text(bot))
