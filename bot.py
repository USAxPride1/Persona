import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

extensions = [
    "cogs.tracking",
    "cogs.simulation",
    "cogs.analysis",
    "cogs.personas"
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is now online.")
    

async def load_extensions():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")


async def main():
    await load_extensions()
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())