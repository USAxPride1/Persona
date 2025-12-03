import discord
from discord.ext import commands
from config import OPENAI_API_KEY, MONGO_URI
from pymongo import MongoClient
from openai import OpenAI

class Analysis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        try:
            self.cluster = MongoClient(MONGO_URI)
            self.db = self.cluster["persona_bot"]
            self.messages = self.db["messages"]
            self.sim_batches = self.db["simulation_batches"]
        except Exception as e:
            print(f"MongoDB connection skipped in Analysis: {e}")
            self.db = None
            self.messages = None
            self.sim_batches = None

        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            print(f"OpenAI client init failed: {e}")
            self.client = None

    def get_insights_channel(self) -> discord.TextChannel | None:
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name == "ai-insights":
                    return channel
        return None

    def build_prompt(self, text_batch: list[str], persona_name: str = "mirror") -> str:
        joined = "\n".join(text_batch)

        try:
            style_block = self.bot.persona_manager.get_persona_style(persona_name)
        except:
            style_block = "You are The Mirror, a neutral psychological observer.\n"

        base = f"""
{style_block}

You will receive a batch of this user's recent Discord messages.
These come from a political / debate / high-intensity server, so expect:
- profanity
- strong opinions
- possibly extreme or socially condemned views

Your job:
- Analyze patterns in tone, emotion, and identity.
- Describe how they tend to communicate.
- Mention their conviction style when appropriate.
- Do NOT argue or give advice.

Messages:
\"\"\"{joined}\"\"\"\

Write a structured analysis under 600 words.
End with one mirror-like sentence.
"""
        return base

    async def _call_openai(self, prompt: str) -> str | None:
        if not self.client:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You analyze user communication patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None

    async def run_realtime_analysis(self, user_id: str, guild_id: str, display_name: str):
        insights_channel = self.get_insights_channel()
        if insights_channel is None:
            print("No #ai-insights channel found.")
            return

        # FIXED
        if self.messages is None:
            await insights_channel.send("⚠️ No database connection for analysis.")
            return

        docs = list(
            self.messages.find(
                {"user_id": user_id, "guild_id": guild_id}
            ).sort("timestamp", -1).limit(250)
        )

        if not docs:
            await insights_channel.send(
                f"⚠️ No messages found for <@{user_id}> to analyze."
            )
            return

        text_batch = [d["content"] for d in docs]

        prompt = self.build_prompt(text_batch, persona_name="mirror")

        await insights_channel.send(
            f"📥 **Collected 250 messages for {display_name}. Running Mirror analysis...**"
        )

        summary = await self._call_openai(prompt)
        if not summary:
            await insights_channel.send("⚠️ Analysis failed (OpenAI issue).")
            return

        await insights_channel.send(
            f"🪞 **The Mirror — Analysis for {display_name} (<@{user_id}>)**\n"
            f"```markdown\n{summary}\n```"
        )

    async def run_simulation_analysis(self, user_id: str, guild_id: str | None = None):
        insights_channel = self.get_insights_channel()
        if insights_channel is None:
            print("No #ai-insights channel found for simulation.")
            return

        # FIXED
        if self.sim_batches is None:
            await insights_channel.send("⚠️ No simulation_batches collection available.")
            return

        entry = self.sim_batches.find_one({"user_id": user_id})
        if not entry or not entry.get("messages"):
            await insights_channel.send(f"⚠️ No simulation batch found for <@{user_id}>.")
            return

        text_batch = entry["messages"]
        prompt = self.build_prompt(text_batch, persona_name="mirror")

        await insights_channel.send(
            f"🧪 **Simulation analysis triggered for <@{user_id}> (The Mirror).**"
        )

        summary = await self._call_openai(prompt)
        if not summary:
            await insights_channel.send("⚠️ Simulation analysis failed (OpenAI issue).")
            return

        await insights_channel.send(
            f"🪞 **The Mirror — Simulation Analysis for <@{user_id}>**\n"
            f"```markdown\n{summary}\n```"
        )

async def setup(bot):
    cog = Analysis(bot)
    await bot.add_cog(cog)
    bot.analysis_cog = cog