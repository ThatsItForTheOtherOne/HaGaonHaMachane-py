import aiohttp
import discord
import json
from sendText import create_embed
import aiosqlite
import re
import textwrap
from bs4 import BeautifulSoup

class Text(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.api_url = "https://www.sefaria.org/api/texts/"
    
    async def parse_sefaria_text(self, sefaria_text):
        footnotes_string = ""

        soup = BeautifulSoup(sefaria_text, "html.parser")
        if "class=\"footnote\"" in sefaria_text:
            for texts in soup.find_all('i', class_='footnote'):
                bolded_text = ""
                bolded = texts.find('b')
                if type(bolded) is not type(None):
                    bolded_text = f"**{bolded.get_text().strip()}**"
                    bolded.decompose()
                footnotes_string += f"\n* {bolded_text}: {texts.get_text()}"
                texts.decompose()
            for texts in soup.find_all('sup'):
                texts.decompose()

        for a in soup.findAll('b'):
            a.replace_with(f"**{a.get_text()}**")
        for a in soup.findAll('i'):
            a.replace_with(f"*{a.get_text()}*")
        for a in soup.findAll('strong'):
            a.replace_with(f"**{a.get_text()}**")

        cleaned_string = f"{soup.text}\n\n{footnotes_string}"
        if len(cleaned_string) < 2048:
            return cleaned_string
        else:
            return soup.text

    async def sefaria_request(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
                if response.status == 404:
                    return None
                return json.loads(body)

    @discord.app_commands.command(name="text", description="Get a Jewish text from Sefaria")
    @discord.app_commands.guild_only
    async def text_command(self, interaction: discord.Interaction, verse: str, hebrew: bool):
        if hebrew:
            key_type = "he"
        else:
            key_type = "text"
        work = re.compile(r"(^[^0-9]*)", re.IGNORECASE).match(verse).groups()
        url = f"{self.api_url}{verse}?context=0{await self.get_translation(interaction, work[0].rstrip())}"
        
        sefaria_obj = await self.sefaria_request(url)
        if 'error' in sefaria_obj:
            await create_embed(interaction, f"Sefaria says: {sefaria_obj['error']}")
            return
        if not key_type in sefaria_obj:
            await create_embed(interaction, "This verse doesn't exist. Check that your input is well formed or that the verse is available in your desired translation.")
        if isinstance(verses := sefaria_obj[key_type], list):
            verse_text = " ".join(verses)
        elif isinstance(verse := sefaria_obj[key_type], str):
            verse_text = verse
        else:
            typeof = type(sefaria_obj[key_type]).__name__
            await create_embed(interaction, f"The Sefaria API returned something that I don't understand ({typeof}). Please contact my administrator about this error.")
            return

        await create_embed(interaction, await self.parse_sefaria_text(verse_text))

    async def get_translation(self, interaction: discord.Interaction, book: str):
        db = await aiosqlite.connect("haGaon.db")
        book = book.replace("_", " ")
        cursor = await db.cursor()
        await cursor.execute(
            """SELECT translation FROM translation WHERE work = ? AND user_id = ?""",
            (book, interaction.user.id),
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

    @discord.app_commands.command(name="get_translation", description="Get Sefaria's translation list for a work")
    @discord.app_commands.guild_only
    async def get_translation_list(self, interaction: discord.Interaction, book: str):
        book = " ".join(book)
        url = f"{self.api_url}{book}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
        sefaria_obj = json.loads(body)
        if 'error' in sefaria_obj:
            await create_embed(interaction, "Sefaria's API has returned an error! Check your parameters!")
            return
        translations = ''
        counter = 1
        for x in sefaria_obj["versions"]:
            if not x["language"] == 'he':
                translations += f'\n {counter} - {x["versionTitle"]}'
                counter += 1
        translation_chunks = textwrap.wrap(translations, 2000, break_long_words=False, replace_whitespace=False)
        for string in translation_chunks:
            await create_embed(interaction, string)

    @discord.app_commands.command(name="set_translation", description="Set your translation for a work from Sefaria")
    @discord.app_commands.guild_only
    async def set_translation(self, interaction, book: str, translation_number: int):
        url = f"{self.api_url}{book.rstrip()}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.text()
        sefaria_obj = json.loads(body)
        if 'error' in sefaria_obj:
            await create_embed(interaction, "Sefaria's API has returned an error! Check your parameters!")
            return
        translation_list = []
        for x in sefaria_obj['versions']:
            if not x['language'] == 'he':
                translation_list.append(x["versionTitle"])
        try:
            translation = translation_list[translation_number - 1]
        except IndexError:
            await create_embed(interaction, "Invalid translation!")
            return
        db = await aiosqlite.connect("haGaon.db")
        cursor = await db.cursor()
        sql = "SELECT * FROM translation WHERE user_id = ?"
        val = (interaction.user.id,)
        await cursor.execute(sql, val)
        result = await cursor.fetchone()
        if result is None:
            sql = "INSERT INTO translation(user_id, work, translation) VALUES(?, ?, ?)"
            val = (interaction.user.id, book.rstrip(), translation)
            await create_embed(interaction, f"Translation for {book.rstrip()} set to {translation} successfully!")
        elif result is not None:
            sql = "UPDATE translation SET work = ?, translation = ? WHERE user_id = ?"
            val = (book.rstrip(), translation, interaction.user.id)
            await create_embed(interaction, f"Translation for {book.rstrip()} updated to {translation} successfully!")
        await cursor.execute(sql, val)
        await db.commit()
        await cursor.close()
        await db.close()
    
async def setup(bot):
    await bot.add_cog(Text(bot), guild=discord.Object(id=858012866383970305))