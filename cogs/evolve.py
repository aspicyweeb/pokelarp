import discord
from discord.ext import commands
import json
import os

class Evolve(commands.Cog):
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

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)

    @commands.command()
    async def grind(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!grind <pokemon>`")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon yet.")
            return

        user = data["users"][user_id]
        found = False
        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                user["grinding"] = p["name"]
                user.setdefault("xp", {})
                user["xp"].setdefault(p["name"], 0)
                found = True
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        self.save_data(data)
        await ctx.send(f"Now grinding **{user['grinding']}**. Every message you send gives it XP!")

    @commands.command()
    async def xp(self, ctx):
        data = self.load_data()
        user = data["users"].get(str(ctx.author.id), {})
        grinding = user.get("grinding")
        if not grinding:
            await ctx.send("You're not grinding anything. Use `!grind <pokemon>`")
            return
        xp = user.get("xp", {}).get(grinding, 0)
        level = (xp // 20) + 1
        await ctx.send(f"Grinding: **{grinding}** | Level: **{level}** | XP: **{xp}**/100")

async def setup(bot):
    await bot.add_cog(Evolve(bot))