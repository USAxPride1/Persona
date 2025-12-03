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

        # If DB is not connected, do NOT crash the bot
        if self.messages is None:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)

        # SAFE DATABASE INSERT — will not crash bot on error
        try:
            self.messages.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "content": message.content,
                "timestamp": message.created_at
            })
        except Exception as e:
            print(f"[Tracking] Mongo insert failed: {e}")
            return

        # Count total messages (XP)
        try:
            total_xp = self.messages.count_documents({
                "user_id": user_id,
                "guild_id": guild_id
            })
        except Exception as e:
            print(f"[Tracking] Mongo count failed: {e}")
            return

        cycle = total_xp % 250

        # Alert #1 — 50 away
        if cycle == 200:
            try:
                await message.channel.send(
                    f"🟦 **{message.author.display_name}, you’re 50 messages away from your Mirror summary! ({total_xp}/250)**"
                )
            except:
                pass

        # Alert #2 — 25 away
        if cycle == 225:
            try:
                await message.channel.send(
                    f"🟧 **{message.author.display_name}, you’re 25 messages away from your Mirror summary! ({total_xp}/250)**"
                )
            except:
                pass

        # Trigger every 250 messages
        if cycle == 0 and total_xp != 0:
            try:
                await message.channel.send(
                    f"📘 **{message.author.display_name} reached {total_xp} messages. Generating Mirror analysis…**"
                )
            except:
                pass

            # Call analysis cog
            try:
                await self.bot.analysis_cog.run_realtime_analysis(
                    user_id=user_id,
                    guild_id=guild_id,
                    display_name=message.author.display_name
                )
            except Exception as e:
                print(f"[Tracking] Analysis trigger failed: {e}")


async def setup(bot):
    await bot.add_cog(Tracking(bot))