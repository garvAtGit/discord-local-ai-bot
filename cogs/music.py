import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}  # guild_id -> deque of (url, title)
        self.loop = {}        # guild_id -> loop boolean

    def get_queue(self, guild_id):
        return self.song_queue.setdefault(guild_id, deque())

    def set_loop(self, guild_id, value: bool):
        self.loop[guild_id] = value

    def get_loop(self, guild_id):
        return self.loop.get(guild_id, False)

    async def play_next(self, guild, vc):
        queue = self.get_queue(guild.id)
        if queue:
            url, title = queue[0]

            def after_play(err):
                if err:
                    print(f"Playback error: {err}")
                if not self.get_loop(guild.id):
                    queue.popleft()
                self.bot.loop.create_task(self.play_next(guild, vc))

            vc.play(discord.FFmpegPCMAudio(
                url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            ), after=after_play)

    @app_commands.command(name="play", description="Play a YouTube song")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        voice = interaction.user.voice
        if not voice or not voice.channel:
            await interaction.followup.send("❌ You must be in a voice channel.")
            return

        vc = interaction.guild.voice_client
        if not vc:
            vc = await voice.channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info['title']
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}")
            return

        queue = self.get_queue(interaction.guild.id)
        queue.append((url, title))

        if not vc.is_playing():
            await self.play_next(interaction.guild, vc)
            await interaction.followup.send(f"🎶 Now playing: **{title}**")
        else:
            await interaction.followup.send(f"✅ Added to queue: **{title}**")

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped.")
        else:
            await interaction.response.send_message("❌ Nothing is playing.")

    @app_commands.command(name="stop", description="Stop and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        if vc:
            self.get_queue(guild_id).clear()
            vc.stop()
            await interaction.response.send_message("🛑 Stopped and cleared the queue.")
        else:
            await interaction.response.send_message("❌ Not connected to a voice channel.")

    @app_commands.command(name="queue", description="Show current song queue")
    async def show_queue(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        if not queue:
            await interaction.response.send_message("📭 Queue is empty.")
        else:
            msg = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queue)])
            await interaction.response.send_message(f"📜 Current Queue:\n{msg}")

    @app_commands.command(name="loop", description="Toggle looping the current song")
    async def toggle_loop(self, interaction: discord.Interaction):
        current = self.get_loop(interaction.guild.id)
        self.set_loop(interaction.guild.id, not current)
        status = "🔁 Looping enabled." if not current else "⏹️ Looping disabled."
        await interaction.response.send_message(status)

    @app_commands.command(name="leave", description="Disconnect the bot from voice")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Disconnected.")
        else:
            await interaction.response.send_message("❌ Not in a voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
