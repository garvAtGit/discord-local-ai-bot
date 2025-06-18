from discord.ext import commands
import discord
import asyncio
import requests
import os
import re
import wikipedia
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWSDATA_API_KEY")


def needs_realtime_data(prompt):
    prompt = prompt.lower()

    # Strong real-time signals
    realtime_keywords = [
        "today", "now", "currently", "latest", "news", "update",
        "happening", "live", "current", "score", "weather", "headline"
    ]
    if any(word in prompt for word in realtime_keywords):
        return True

    # Question patterns indicating recent events
    realtime_patterns = [
        r"when did .+ happen",
        r"what happened (in|with|to) .+",
        r"(did|has) .+ (attack|declare|explode|launch|collapse|crash|strike|happen)",
        r"(is|are|was|were) .+ (ongoing|happening|under attack)",
        r"(who|what|where|when) (attacked|exploded|collapsed|died|killed|won)",
        r"(breaking|urgent) news"
    ]

    for pattern in realtime_patterns:
        if re.search(pattern, prompt):
            return True

    return False



def extract_news_topic(prompt):
    stopwords = {
        "did", "does", "do", "is", "are", "was", "were", "the", "a", "an",
        "in", "on", "at", "to", "for", "of", "and", "or", "with", "by", "about", "today"
    }
    words = [w for w in re.findall(r'\w+', prompt.lower()) if w not in stopwords]
    return " ".join(words)


def fetch_latest_news(topic=None):
    try:
        if not NEWS_API_KEY:
            return "❌ News API key not set."
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&language=en"
        if topic:
            url += f"&q={topic}"
        res = requests.get(url)
        data = res.json()
        articles = data.get("results", [])[:5]
        seen = set()
        news_lines = []
        for a in articles:
            title = a['title']
            if title not in seen:
                news_lines.append(f"- {title}")
                seen.add(title)
        if not news_lines:
            return "No news articles found."
        if topic:
            return f"🗞️ Latest headlines for '{topic}':\n" + "\n".join(news_lines)
        else:
            return f"🗞️ Latest headlines:\n" + "\n".join(news_lines)
    except Exception:
        return "❌ Could not fetch news."


def fetch_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=3)
    except Exception:
        return None


async def run_ollama(prompt):
    try:
        process = await asyncio.create_subprocess_shell(
            f'ollama run mistral "{prompt}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode().strip() or "⚠️ The AI didn't return any response."
    except Exception as e:
        return f"❌ Exception: {str(e)}"


class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ask")
    async def ask(self, ctx, *, prompt: str):
        thinking_msg = await ctx.send("🧠 Thinking...")

        # Step 1: Check for real-time data needs
        if needs_realtime_data(prompt):
            await thinking_msg.edit(content="🌐 Fetching real-time info...")
            topic = extract_news_topic(prompt)
            news_result = fetch_latest_news(topic)

            if "No news articles found." in news_result or len(news_result.splitlines()) <= 2:
                await thinking_msg.edit(content="📚 No recent news. Checking historical info...")
                wiki_result = fetch_wikipedia_summary(topic)
                if wiki_result:
                    response = wiki_result
                else:
                    response = await run_ollama(prompt)
            else:
                response = news_result
        else:
            # Step 2: Fallback to local model
            response = await run_ollama(prompt)

        # Step 3: Send response
        if len(response) > 2000:
            response = response[:1997] + "..."

        await ctx.send(response)
        await thinking_msg.delete()

@commands.Cog.listener()
async def on_message(self, message):
    if message.author.bot:
        return

    # Prevent double-response if it's a command
    prefixes = await self.bot.get_prefix(message)
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    if any(message.content.strip().startswith(prefix) for prefix in prefixes):
        return

    # Respond to replies to the bot only (non-command)
    if (
        message.reference and message.reference.resolved and
        message.reference.resolved.author.id == self.bot.user.id
    ):
        ctx = await self.bot.get_context(message)
        await self.ask(ctx, prompt=message.content)

    # Allow command handling
    await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(AIChat(bot))
