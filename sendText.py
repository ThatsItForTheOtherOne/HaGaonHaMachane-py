import discord

async def create_embed(interaction: discord.Interaction, text):
    if len(text) > 2048:
        await interaction.response.send_message("MESSAGE TOO LONG!")
        return
    embed = discord.Embed(description=text, color=0x0000FF)
    embed.set_footer(
        text=interaction.client.description,
        icon_url="https://cdn.discordapp.com/avatars/466676353907818516/c48b21b283307d9ff454ed221dc0aaa2.jpg?size=1024",
    )
    await interaction.response.send_message(embed=embed)
