import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # <-- REQUIRED
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        extensions = ['cogs.welcome', 'cogs.music', 'cogs.ai_chat', 'cogs.news', 'cogs.insta_post', 'cogs.moderation']
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded: {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())