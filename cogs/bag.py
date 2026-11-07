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
                data = json.load(f)
                data.setdefault("users", {})
                return data
        return {"users": {}}

    def get_sprite(self, dex_num, shiny=False):
        if shiny:
            return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{dex_num}.png"
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

    @commands.command()
    async def bag(self, ctx):
        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet! Try `!starter`")
            return

        user = data["users"][user_id]
        lines = []
        seen = {}
        for p in user["pokemon"]:
            key = p["name"]
            if key not in seen:
                level = user.get("levels", {}).get(key, 1)
                shiny = "✨ " if p.get("shiny") else ""
                nick = f" ({p['nickname']})" if p.get("nickname") else ""
                lines.append(f"{shiny}**{key}**{nick} — Lv.{level}")
                seen[key] = True

        text = "\n".join(lines) if lines else "None"
        coins = user.get("coins", 0)
        balls = user.get("inventory", {}).get("ball", 0)
        text += f"\n\n**Coins:** {coins}\n**Poké Balls:** {balls}"

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Pokémon", description=text, color=0xFF69B4)
        await ctx.send(embed=embed)

    @commands.command()
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

        grinding = user.get("grinding")
        xp = user.get("xp", {}).get(found["name"], 0)
        xp_text = f"\nXP: **{xp}**/100" if grinding == found["name"] else ""

        embed = discord.Embed(
            title=f"{'✨ ' if shiny else ''}{display}",
            description=f"**{found['name']}** — Level {level}{xp_text}",
            color=0xFFD700 if shiny else 0xFF69B4
        )
        embed.set_image(url=sprite)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bag(bot))