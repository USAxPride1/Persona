import discord
from discord.ext import commands
from discord import app_commands
from config import MONGO_URI
from pymongo import MongoClient

class Simulation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        try:
            self.cluster = MongoClient(MONGO_URI)
            self.db = self.cluster["persona_bot"]
            self.sim_batches = self.db["simulation_batches"]
            self.messages = self.db["messages"]
        except Exception as e:
            print(f"MongoDB connection skipped in Simulation: {e}")
            self.db = None
            self.sim_batches = None
            self.messages = None

    def get_insights_channel(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name == "ai-insights":
                    return channel
        return None

    @app_commands.command(
        name="simulate_messages",
        description="Save the last N messages from ANY user as a simulation batch."
    )
    async def simulate_messages(
        self,
        interaction: discord.Interaction,
        target_user: discord.Member,
        amount: int = 100
    ):
        await interaction.response.defer(ephemeral=True)

        # FIXED: boolean test on collections
        if self.messages is None or self.sim_batches is None:
            await interaction.followup.send("⚠️ Database not available.", ephemeral=True)
            return

        user_id = str(target_user.id)
        guild_id = str(interaction.guild_id)

        docs = list(
            self.messages.find(
                {"user_id": user_id, "guild_id": guild_id}
            ).sort("timestamp", -1).limit(amount)
        )

        text_batch = [d["content"] for d in docs]

        self.sim_batches.update_one(
            {"user_id": user_id},
            {"$set": {"messages": text_batch}},
            upsert=True
        )

        await interaction.followup.send(
            f"Simulation batch saved for **{target_user.display_name}** with **{len(text_batch)}** messages.",
            ephemeral=True
        )

        insights = self.get_insights_channel()
        if insights:
            preview = "\n".join(text_batch[:10]) if text_batch else "No messages found."
            await insights.send(
                f"🔧 **Simulation batch updated for {target_user.display_name}**\n"
                f"Total messages in batch: **{len(text_batch)}**\n\n"
                f"**Preview (first 10):**\n```{preview}```"
            )

    @app_commands.command(
        name="simulate_analysis",
        description="Run Mirror analysis on ANY user’s saved simulation batch."
    )
    async def simulate_analysis(
        self,
        interaction: discord.Interaction,
        target_user: discord.Member
    ):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            f"Running simulation analysis for **{target_user.display_name}**… check **#ai-insights**.",
            ephemeral=True
        )

        try:
            await self.bot.analysis_cog.run_simulation_analysis(
                user_id=str(target_user.id),
                guild_id=str(interaction.guild_id)
            )
        except Exception as e:
            insights = self.get_insights_channel()
            if insights:
                await insights.send(f"⚠️ Error running simulation analysis: {e}")

async def setup(bot):
    await bot.add_cog(Simulation(bot))