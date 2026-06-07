import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

    canal = bot.get_channel(1513230063225671750)

    if canal:
        await canal.send(
            "✅ Bot conectado correctamente desde Railway."
        )

bot.run(TOKEN)
