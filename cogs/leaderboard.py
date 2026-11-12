import discord
from discord.ext import commands

import cogs as storage


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        users = storage.data.get("users", {})
        scores = []
        for uid, user in users.items():
            count = len(user.get("pokemon", []))
            if count > 0:
                scores.append((uid, count))
        if not scores:
            await ctx.send("No one has caught anything yet!")
            return

        scores.sort(key=lambda row: row[1], reverse=True)
        lines = []
        for index, (uid, count) in enumerate(scores[:10], 1):
            name = await self.display_name(ctx, uid)
            lines.append(f"**{index}.** {name} — {count} caught")

        embed = discord.Embed(title="Top Catchers", description="\n".join(lines), color=0xFF69B4)
        await ctx.send(embed=embed)

    async def display_name(self, ctx, uid):
        try:
            user_id = int(uid)
        except ValueError:
            return "Unknown"
        if ctx.guild is not None:
            member = ctx.guild.get_member(user_id)
            if member is not None:
                return member.display_name
        user = self.bot.get_user(user_id)
        if user is None:
            try:
                user = await self.bot.fetch_user(user_id)
            except discord.HTTPException:
                user = None
        if user is None:
            return f"User {uid[-4:]}"
        return user.display_name


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))