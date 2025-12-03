import discord
from discord.ext import commands
import asyncio
import logging
from config import DISCORD_TOKEN

# Clean logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)
logging.getLogger("discord.bot").setLevel(logging.INFO)

# ---------- Bot Setup ----------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

COGS = [
    "cogs.tracking",
    "cogs.personas",
    "cogs.simulation",
    "cogs.analysis",
]


async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded extension: {cog}")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")


@bot.tree.command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓", ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    print("Clearing existing global slash commands...")

    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print("🔥 Cleared all global slash commands.")
    except Exception as e:
        print("❌ Clear FAILED:", e)

    print("⏳ Attempting to sync fresh slash commands...")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print("❌ Sync FAILED:", e)

    print("Bot is now online.")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())