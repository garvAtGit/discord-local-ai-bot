from discord.ext import commands
from discord import Member, File, Embed
import discord
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        guild = member.guild

        # ✅ Find welcome channel by name
        channel = discord.utils.get(guild.text_channels, name="❃︱yolo-welcome")
        if not channel:
            print("❌ Welcome channel not found.")
            return

        # ✅ Generate welcome image
        avatar_asset = member.display_avatar.replace(size=128)
        buffer = BytesIO(await avatar_asset.read())

        base = Image.new("RGB", (600, 200), (30, 30, 30))
        draw = ImageDraw.Draw(base)

        # Circle avatar
        avatar = Image.open(buffer).convert("RGB").resize((128, 128))
        mask = Image.new("L", avatar.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 128, 128), fill=255)
        avatar.putalpha(mask)
        base.paste(avatar, (30, 36), avatar)

        # Text
        font_path = "arial.ttf"  # replace with custom if needed
        try:
            font = ImageFont.truetype(font_path, 28)
        except:
            font = ImageFont.load_default()

        draw.text((180, 60), f"Welcome, {member.name}!", font=font, fill=(255, 255, 255))
        draw.text((180, 100), f"to {guild.name}", font=font, fill=(200, 200, 200))

        image_bytes = BytesIO()
        base.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        file = File(image_bytes, filename="welcome.png")

        # ✅ Embed message
        embed = Embed(
            title=f"🎉 Welcome {member.name}!",
            description=f"Glad to have you here in **{guild.name}**!\nSpread the love by sharing our server invite link.",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://welcome.png")

        await channel.send(embed=embed, file=file)

# Async setup
async def setup(bot):
    await bot.add_cog(Welcome(bot))
