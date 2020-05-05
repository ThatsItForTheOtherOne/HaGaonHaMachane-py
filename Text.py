import discord
from discord.ext import commands
import json
from urllib.request import urlopen
import re
from sendText import createEmbed
from aiohttp import ClientSession


def cleanHtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = ClientSession(loop=bot.loop)
        self.api_url = 'https://www.sefaria.org/api/texts/'
    
    @commands.command(name="text")
    async def Text(self, ctx, *verse):
            verse = ' '.join(verse)
            if(verse.count(' ') > 1): verse = verse.replace(" ", "_", 1)
            if('-' in verse): 
                    exp = re.compile(r'(\S+)\s(\S+):(\d+)-(\d+)', re.IGNORECASE)
                    e = exp.match(verse).groups()
                    sefaria_obj = json.load(urlopen(self.api_url + e[0] + '.' + e[1] + '.' + e[2]))
                    versetext = ''
                    for x in range(int(e[2])-1, int(e[3])):
                            versetext = versetext + ' ' + sefaria_obj['text'][x]
                    await createEmbed(ctx, cleanHtml(versetext))
            else:
                    exp = re.compile(r'(\S+)\s(\S+):(\d+)', re.IGNORECASE)
                    e = exp.match(verse).groups()
                    sefaria_obj = json.load(urlopen(self.api_url + e[0] + '.' + e[1] + '.' + e[2] + '?context=0')) 
                    await createEmbed(ctx, cleanHtml(sefaria_obj['text']))
def setup(bot):
    bot.add_cog(Text(bot))
