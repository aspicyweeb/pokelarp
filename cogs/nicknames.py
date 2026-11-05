import discord
from discord.ext import commands

class Nicknames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nickname(self, ctx, pokemon: str = None, *, nick: str = None):
        if not pokemon or not nick:
            await ctx.send("Usage: `!nickname <pokemon> <new name>`")
            return

        # Assumes data is accessible via bot or a shared store
        # For now this is a stub — wire it to your data dict
        await ctx.send(f"Nickname feature ready. (Connect to your data store)")

async def setup(bot):
    await bot.add_cog(Nicknames(bot))
