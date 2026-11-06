import discord
from discord.ext import commands
import json
import os

class Release(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {"users": {}}

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)

    @commands.command()
    async def release(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!release <pokemon>`")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return

        user = data["users"][user_id]
        for i, p in enumerate(user["pokemon"]):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                removed = user["pokemon"].pop(i)
                self.save_data(data)
                await ctx.send(f"Released your **{removed['name']}**.")
                return

        await ctx.send(f"You don't have a {name} to release.")

async def setup(bot):
    await bot.add_cog(Release(bot))
