import discord
from discord.ext import commands
import requests

API_KEY = 'pub_e8fb6596233547faa4e1cac4b114fdee'  # Replace with your API key

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='news')
    async def get_news(self, ctx, *, country='world'):
        """Fetch latest world news. Optionally provide a country (e.g., 'us', 'in')."""
        url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&country={country}&language=en&category=top"

        try:
            response = requests.get(url)
            data = response.json()

            articles = data.get("results", [])[:3]  # top 3 articles

            if not articles:
                await ctx.send("❌ Couldn't fetch any news.")
                return

            embed = discord.Embed(
                title=f"🗞️ Top News Headlines ({country.upper()})",
                color=discord.Color.orange()
            )

            for article in articles:
                title = article["title"]
                link = article["link"]
                embed.add_field(name=title, value=f"[Read more]({link})", inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching news: {e}")

async def setup(bot):
    await bot.add_cog(News(bot))
