import discord
from discord.ext import commands
import asyncio
import logging
from config import DISCORD_TOKEN

# Enable debug logging so sync errors show in Railway logs
logging.basicConfig(level=logging.INFO)

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

    # 🔥 TEMP FIX: Clear old slash commands from Discord
    try:
        print("Clearing existing global slash commands...")
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print("🔥 Cleared all global slash commands.")
    except Exception as e:
        print("❌ Clear failed:", e)

    # Now sync ALL commands cleanly
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print("❌ Sync failed:", e)

    print("Bot is now online.")


# ---------- Runner ----------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())