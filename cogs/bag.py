import discord
from discord.ext import commands

class Bag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bag(self, ctx):
        await ctx.send("Improved bag (levels + shinies) ready. (Connect to data)")

    @commands.command()
    async def info(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!info <pokemon>`")
            return
        await ctx.send(f"Info for {name} ready. (Connect to data)")

async def setup(bot):
    await bot.add_cog(Bag(bot))
