import discord
from discord.ext import commands
import json
import os

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {"users": {}}

    @commands.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        data = self.load_data()
        users = data.get("users", {})
        if not users:
            await ctx.send("No one has caught anything yet!")
            return

        scores = []
        for uid, user in users.items():
            count = len(user.get("pokemon", []))
            if count > 0:
                scores.append((uid, count))

        scores.sort(key=lambda x: x[1], reverse=True)
        top = scores[:10]

        lines = []
        for i, (uid, count) in enumerate(top, 1):
            try:
                member = ctx.guild.get_member(int(uid))
                name = member.display_name if member else f"User {uid[-4:]}"
            except:
                name = f"User {uid[-4:]}"
            lines.append(f"**{i}.** {name} — {count} caught")

        embed = discord.Embed(
            title="Top Catchers",
            description="\n".join(lines) if lines else "None yet",
            color=0xFF69B4
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
