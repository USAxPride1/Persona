import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed for tracking & simulations

bot = commands.Bot(command_prefix="!", intents=intents)

# List of cogs you are using
extensions = [
    "cogs.tracking",
    "cogs.simulation",
    "cogs.analysis",
    "cogs.personas"
]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Syncing slash commands…")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    print("Bot is now online.")


async def load_extensions():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Failed to load {ext}: {e}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Fallback for environments with already-running event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())