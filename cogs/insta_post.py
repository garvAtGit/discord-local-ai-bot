from discord.ext import commands
from discord import File
import yt_dlp
import aiohttp
import asyncio
import subprocess
import os
from io import BytesIO

class InstaPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="post")
    async def post(self, ctx, link: str):
        temp_video = "temp_instagram_video.mp4"
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': temp_video,
            'merge_output_format': 'mp4',
            'quiet': True,
            'nocheckcertificate': True,
        }

        # Step 1: Download & merge video+audio
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            await ctx.send(f"❌ Failed to download video: {e}")
            return

        # Step 2: Upload to Discord
        try:
            with open(temp_video, "rb") as f:
                await ctx.send(file=File(f, filename="video.mp4"))
        except Exception as e:
            await ctx.send(f"❌ Error sending video: {e}")
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)

# Async setup
async def setup(bot):
    await bot.add_cog(InstaPost(bot))
