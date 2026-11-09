import discord
from discord.ext import commands
import json
import os

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                data = json.load(f)
                data.setdefault("users", {})
                data.setdefault("trades", {})
                return data
        return {"users": {}, "trades": {}}

    def save_data(self, data):
        # Nuclear option — main bot handles all saves
        pass

    @commands.command()
    async def trade(self, ctx, member: discord.Member = None):
        await ctx.send("Trading is temporarily disabled while we fix saving.")

    @commands.command()
    async def offer(self, ctx, *, name: str = None):
        await ctx.send("Trading is temporarily disabled while we fix saving.")

    @commands.command()
    async def confirm(self, ctx):
        await ctx.send("Trading is temporarily disabled while we fix saving.")

    @commands.command()
    async def cancel(self, ctx):
        await ctx.send("Trading is temporarily disabled while we fix saving.")

async def setup(bot):
    await bot.add_cog(Trade(bot))