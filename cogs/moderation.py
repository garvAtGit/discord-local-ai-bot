import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        await channel.send(message)
        await ctx.send(f"📨 Sent message to {channel.mention}")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 Kicked {member.mention} for: {reason}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Banned {member.mention} for: {reason}")

    @commands.command(name="role")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"✅ Assigned role **{role.name}** to {member.mention}")

    @say.error
    @kick.error
    @ban.error
    @role.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don’t have permission to do that.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Couldn't find the member/channel/role. Please mention them properly.")
        else:
            await ctx.send(f"⚠️ Error: {error}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
