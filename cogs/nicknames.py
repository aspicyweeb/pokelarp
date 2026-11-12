from discord.ext import commands

import cogs as storage
from cogs import find_owned


class Nicknames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nickname(self, ctx, *, text: str = None):
        if not text or " " not in text.strip():
            await ctx.send("Usage: `!nickname <pokemon> <new name>`")
            return
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You don't have any Pokémon yet.")
            return
        mon, nick = split_target(user, text)
        if mon is None or not nick:
            await ctx.send("Usage: `!nickname <pokemon> <new name>` — use the species or current nickname.")
            return
        nick = " ".join(nick.split())
        if not nick or len(nick) > 32 or "@" in nick:
            await ctx.send("Nicknames have to be 1–32 characters and can't include @.")
            return
        mon["nickname"] = nick
        storage.save()
        await ctx.send(f"Nicknamed your {mon['name']} to **{nick}**!")


def split_target(user, text):
    words = text.split()
    for size in range(len(words) - 1, 0, -1):
        mon = find_owned(user, " ".join(words[:size]))
        if mon is not None:
            return mon, " ".join(words[size:])
    return None, None


async def setup(bot):
    await bot.add_cog(Nicknames(bot))