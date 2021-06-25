import aiohttp
import discord
from discord.ext import commands
import json
from sendText import create_embed
from aiohttp import ClientSession
import aiosqlite
import re
import textwrap

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
        verse = ' '.join(verse)
        work = re.compile(r"(^[^0-9]*)", re.IGNORECASE).match(verse).groups()
        url = f"{self.api_url}{verse}?context=0{await self.get_translation(ctx, work[0].rstrip())}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status == 404:
                    await create_embed(ctx, "Sefaria has sent an unknown response, is your verse correct?")
                    return
                sefaria_obj = json.loads(body)
        if not key_type in sefaria_obj:
            await create_embed(ctx, "This verse doesn't exist. Check that your input is well formed or that the verse is available in your desired translation.")
        if isinstance(verses := sefaria_obj[key_type], list):
            verse_text = " ".join(verses)
        elif isinstance(verse := sefaria_obj[key_type], str):
            verse_text = verse
        else:
            typeof = type(sefaria_obj[key_type]).__name__
            await create_embed(ctx, f"The Sefaria API returned something that I don't understand ({typeof}). Please contact my administrator about this error.")
            return

        await create_embed(ctx, await self.parse_sefaria_text(verse_text))

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
    
    async def get_translation_list(self, ctx, *book):
        book = " ".join(book)
        url = f"{self.api_url}{book}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
        sefaria_obj = json.loads(body)
        if 'error' in sefaria_obj:
            await create_embed(ctx, "Sefaria's API has returned an error! Check your parameters!")
            return
        translations = ''
        counter = 1
        for x in sefaria_obj["versions"]:
            if not x["language"] == 'he':
                translations += f'\n {counter} - {x["versionTitle"]}'
                counter += 1
        translation_chunks = textwrap.wrap(translations, 2000, break_long_words=False, replace_whitespace=False)
        for string in translation_chunks:
            await create_embed(ctx, string)

    async def set_translation(self, ctx, *parameters):
        parameters = " ".join(parameters)
        try:
            parameters = re.compile(r"([^\d]+)(.*)", re.IGNORECASE).match(parameters).groups()
        except:
            await create_embed(ctx, f"An internal error occured! Check your parameters or try later!")
        url = f"{self.api_url}{parameters[0].rstrip()}"
        if(parameters[1] == ''):
            await create_embed(ctx, f"An internal error occured! Check your parameters or try later!")
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
        sefaria_obj = json.loads(body)
        if 'error' in sefaria_obj:
            await create_embed(ctx, "Sefaria's API has returned an error! Check your parameters!")
            return
        translation_list = []
        for x in sefaria_obj['versions']:
            if not x['language'] == 'he':
                translation_list.append(x["versionTitle"])
        try:
            translation = translation_list[int(parameters[1]) - 1]
        except IndexError:
            await create_embed(ctx, "Invalid translation!")
            return
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        sql = "SELECT * FROM translation WHERE user_id = ?"
        val = (ctx.message.author.id,)
        await cursor.execute(sql, val)
        result = await cursor.fetchone()
        if result is None:
            sql = "INSERT INTO translation(user_id, work, translation) VALUES(?, ?, ?)"
            val = (ctx.message.author.id, parameters[0].rstrip(), translation)
            await create_embed(ctx, f"Translation for {parameters[0].rstrip()} set to {translation} successfully!")
        elif result is not None:
            sql = "UPDATE translation SET work = ?, translation = ? WHERE user_id = ?"
            val = (parameters[0].rstrip(), translation, ctx.message.author.id)
            await create_embed(ctx, f"Translation for {parameters[0].rstrip()} updated to {translation} successfully!")
        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(name="hebrewText", aliases=['hebrew_text', 'hebrewtext'])
    async def hebrew_text_command(self, ctx, *verse):
        await self.text_command(ctx, *verse)

    @commands.command(name="text")
    async def regular_text_command(self, ctx, *verse):
        await self.text_command(ctx, *verse)

    @commands.command(name="setTranslation", aliases=['settranslation', 'set_translation'])
    async def set_translation_command(self, ctx, *string):
        await self.set_translation(ctx, *string)
    
    @commands.command(name="getTranslations", aliases=['gettranslations', 'get_translations'])
    async def get_translation_list_command(self, ctx, *string):
        await self.get_translation_list(ctx, *string)

def setup(bot):
    bot.add_cog(Text(bot))