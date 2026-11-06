import discord
from discord.ext import commands
import json
import os

class Pokedex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {"users": {}}

    @commands.command(aliases=["dex", "pokedex"])
    async def pokedex(self, ctx):
        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        caught = {p["name"] for p in data["users"][user_id]["pokemon"]}
        total = 151
        count = len(caught)
        percent = round((count / total) * 100, 1)

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Pokédex",
            description=f"**{count}/{total}** Pokémon caught ({percent}%)",
            color=0xFF69B4
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pokedex(bot))
