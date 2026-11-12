import discord
from discord.ext import commands

import cogs as storage
from cogs import find_owned


class Gift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gift(self, ctx, member: discord.Member = None, *, name: str = None):
        if member is None or not name:
            await ctx.send("Usage: `!gift @user <pokemon>`")
            return
        if member.bot or member.id == ctx.author.id:
            await ctx.send("Pick a real person who isn't you.")
            return

        giver = storage.data.get("users", {}).get(str(ctx.author.id))
        if not giver or not giver.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return
        mon = find_owned(giver, name)
        if mon is None:
            await ctx.send(f"You don't have a {name}.")
            return
        if storage.mon_offered(mon):
            await ctx.send("That Pokémon is offered in a trade. `!cancel` the trade first.")
            return

        removed = storage.pop_pokemon(giver, lambda other: other is mon)
        if removed is None:
            await ctx.send(f"You don't have a {name}.")
            return
        receiver = storage.ensure_user(member.id)
        receiver["pokemon"].append(removed)
        storage.save()
        await ctx.send(
            f"**{ctx.author.display_name}** gifted **{removed['name']}** to **{member.display_name}**."
        )


async def setup(bot):
    await bot.add_cog(Gift(bot))