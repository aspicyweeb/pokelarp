import discord
from discord.ext import commands
import json
import os

class Profile(commands.Cog):
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

    @commands.command(aliases=["me", "profile"])
    async def profile(self, ctx):
        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        user = data["users"][user_id]
        pokemon = user.get("pokemon", [])
        total = len(pokemon)
        unique = len({p["name"] for p in pokemon})

        # Starter
        starter = "None"
        for p in pokemon:
            if p.get("name") in ["Bulbasaur", "Charmander", "Squirtle"]:
                starter = p["name"]
                break

        # Highest level
        levels = user.get("levels", {})
        highest = "None"
        if levels:
            top_name = max(levels, key=levels.get)
            highest = f"{top_name} (Lv.{levels[top_name]})"

        # Grinding
        grinding = user.get("grinding", "None")
        xp = user.get("xp", {}).get(grinding, 0) if grinding != "None" else 0
        grind_text = f"{grinding} ({xp}/100 XP)" if grinding != "None" else "None"

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Profile",
            color=0xFF69B4
        )
        embed.add_field(name="Starter", value=starter, inline=True)
        embed.add_field(name="Total Caught", value=str(total), inline=True)
        embed.add_field(name="Unique", value=f"{unique}/151", inline=True)
        embed.add_field(name="Highest Level", value=highest, inline=True)
        embed.add_field(name="Grinding", value=grind_text, inline=True)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))