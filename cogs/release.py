from discord.ext import commands

import cogs as storage
from cogs import find_owned


class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def release(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!release <pokemon>`")
            return
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return
        mon = find_owned(user, name)
        if mon is None:
            await ctx.send(f"You don't have a {name} to release.")
            return
        if storage.mon_offered(mon):
            await ctx.send("That Pokémon is offered in a trade. `!cancel` the trade first.")
            return
        removed = storage.pop_pokemon(user, lambda other: other is mon)
        if removed is None:
            await ctx.send(f"You don't have a {name} to release.")
            return
        storage.save()
        await ctx.send(f"Released your **{removed['name']}**.")


async def setup(bot):
    await bot.add_cog(Release(bot))