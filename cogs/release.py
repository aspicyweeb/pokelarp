import discord
from discord.ext import commands

class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def release(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!release <pokemon>`")
            return
        await ctx.send(f"Release feature ready for {name}. (Connect to data)")

async def setup(bot):
    await bot.add_cog(Release(bot))
