import discord
from discord.ext import commands
from config import MONGO_URI
from pymongo import MongoClient

class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        try:
            self.cluster = MongoClient(MONGO_URI)
            self.db = self.cluster["persona_bot"]
            self.messages = self.db["messages"]
        except Exception as e:
            print(f"MongoDB connection skipped in Tracking: {e}")
            self.db = None
            self.messages = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # ignore bots
        if message.author.bot:
            return

        # ignore DMs
        if isinstance(message.channel, discord.DMChannel):
            return

        # ignore non-text content
        if message.attachments or message.embeds or message.stickers:
            return
        if not message.content or message.content.strip() == "":
            return

        if not self.messages:
            # DB not available yet, just skip storing
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)

        # store message
        try:
            self.messages.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "content": message.content,
                "timestamp": message.created_at
            })
        except Exception:
            # safe fail
            return

        # count total messages (XP)
        try:
            total_xp = self.messages.count_documents({
                "user_id": user_id,
                "guild_id": guild_id
            })
        except Exception:
            total_xp = 0

        # use modulo so this works every 250 messages, not just once
        cycle = total_xp % 250

        # Alert #1 — 50 away (i.e., at 200, 450, 700, ...)
        if cycle == 200:
            try:
                await message.channel.send(
                    f"🟦 **{message.author.display_name}, you’re 50 messages away from your Mirror summary! ({total_xp}/250)**"
                )
            except Exception:
                pass

        # Alert #2 — 25 away (225, 475, 725, ...)
        if cycle == 225:
            try:
                await message.channel.send(
                    f"🟧 **{message.author.display_name}, you’re 25 messages away from your Mirror summary! ({total_xp}/250)**"
                )
            except Exception:
                pass

        # Trigger — every 250 messages (250, 500, 750, ...)
        if cycle == 0 and total_xp != 0:
            try:
                await message.channel.send(
                    f"📘 **{message.author.display_name} reached {total_xp} messages. Generating Mirror analysis…**"
                )
            except Exception:
                pass

            # call the analysis cog
            try:
                await self.bot.analysis_cog.run_realtime_analysis(
                    user_id=user_id,
                    guild_id=guild_id,
                    display_name=message.author.display_name
                )
            except Exception as e:
                print(f"Error triggering realtime analysis: {e}")

async def setup(bot):
    await bot.add_cog(Tracking(bot))