import discord
from discord.ext import commands
import cogs as storage


class Grind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def grind(self, ctx, *, name: str = None):
        user = storage.ensure_user(ctx.author.id)
        if not name:
            mon = storage.get_grinder(user)
            if mon:
                lv = storage.mon_level(user, mon)
                xp = mon.get("xp", 0)
                needed = storage.xp_for_level(lv)
                await ctx.send(f"Grinding **{mon['name']}** — Lv.{lv} ({xp}/{needed} XP)")
            else:
                await ctx.send("Not grinding anything. Use `!grind <pokemon>`")
            return
        if name.lower() == "clear":
            storage.set_grinder(user, None)
            storage.save()
            await ctx.send("Stopped grinding.")
            return
        mon = storage.find_owned(user, name)
        if not mon:
            await ctx.send("You don't have that Pokémon.")
            return
        storage.set_grinder(user, mon)
        storage.save()
        await ctx.send(f"Now grinding **{mon['name']}**.")

    @commands.command(aliases=["lvl", "level"])
    async def levels(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        user = storage.ensure_user(target.id)
        mons = user.get("pokemon", [])
        if not mons:
            await ctx.send("No Pokémon.")
            return
        sorted_mons = sorted(mons, key=lambda m: storage.mon_level(user, m), reverse=True)[:8]
        lines = [f"**{m['name']}** — Lv.{storage.mon_level(user, m)}" for m in sorted_mons]
        embed = discord.Embed(
            title=f"{target.display_name}'s Levels",
            description="\n".join(lines),
            color=0xFF69B4,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Grind(bot))