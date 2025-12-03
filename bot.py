import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN

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


# ---------- Auto Slash Sync ----------
async def sync_slash_commands():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print("Slash command sync failed:", e)


# ---------- Test Slash Command (/ping) ----------
@bot.tree.command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓", ephemeral=True)


# ---------- Events ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Syncing slash commands…")
    await sync_slash_commands()
    print("Bot is now online.")


# ---------- Runner ----------
async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


asyncio.run(main())