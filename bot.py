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
intents.message_content = True  # required for tracking cog

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


# ---------- Load All Cogs ----------
async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded extension: {cog}")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")


# ---------- Test Slash Command (/ping) ----------
@bot.tree.command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓", ephemeral=True)


# ---------- Events ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Full wipe of commands (global + guild)
    print("Clearing ALL slash commands (global + guild)...")

    try:
        bot.tree.clear_commands(guild=None)
        for guild in bot.guilds:
            bot.tree.clear_commands(guild=guild)

        await bot.tree.sync()
        print("🔥 Cleared all commands globally AND per guild.")
    except Exception as e:
        print("❌ Clear FAILED:", e)

    # Sync fresh commands
    print("⏳ Attempting to sync fresh commands...")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        print("❌ Sync FAILED:", e)

    print("Bot is now online.")


# ---------- Runner ----------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())