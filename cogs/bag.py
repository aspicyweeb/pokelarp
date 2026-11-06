import discord
from discord.ext import commands
import json
import os

class Bag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {"users": {}}

    def get_sprite(self, dex_num, shiny=False):
        if shiny:
            return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{dex_num}.png"
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

    @commands.command(name="info")
    async def info(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!info <pokemon>`")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"]:
            await ctx.send("You don't have any Pokémon yet.")
            return

        user = data["users"][user_id]
        found = None
        for p in user.get("pokemon", []):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                found = p
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        level = user.get("levels", {}).get(found["name"], 1)
        shiny = found.get("shiny", False)
        nick = found.get("nickname")
        display = nick if nick else found["name"]
        sprite = self.get_sprite(found["dex"], shiny)

        embed = discord.Embed(
            title=f"{'✨ ' if shiny else ''}{display}",
            description=f"**{found['name']}** — Level {level}",
            color=0xFFD700 if shiny else 0xFF69B4
        )
        embed.set_image(url=sprite)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bag(bot))
