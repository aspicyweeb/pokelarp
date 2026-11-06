import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spawnrate(self, ctx, min_minutes: int = None, max_minutes: int = None):
        if min_minutes is None or max_minutes is None:
            await ctx.send(f"Current spawn rate: **{self.bot.MIN_SPAWN_MINUTES}–{self.bot.MAX_SPAWN_MINUTES}** minutes\n"
                           f"Usage: `!spawnrate <min> <max>`")
            return

        if min_minutes < 5 or max_minutes < min_minutes:
            await ctx.send("Min must be at least 5 and max must be higher than min.")
            return

        self.bot.MIN_SPAWN_MINUTES = min_minutes
        self.bot.MAX_SPAWN_MINUTES = max_minutes
        await ctx.send(f"Spawn rate updated to **{min_minutes}–{max_minutes}** minutes.")

    @spawnrate.error
    async def spawnrate_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Only admins can change the spawn rate.")

async def setup(bot):
    await bot.add_cog(Admin(bot))