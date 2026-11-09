import discord
from discord.ext import commands
import json
import os

class Gift(commands.Cog):
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
        # Nuclear option — main bot handles all saves
        pass

    def ensure_user(self, data, user_id):
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "pokemon": [],
                "levels": {},
                "has_starter": False,
                "catches_without_starter": 0,
                "coins": 0,
                "inventory": {}
            }
        user = data["users"][user_id]
        user.setdefault("pokemon", [])
        user.setdefault("levels", {})
        user.setdefault("coins", 0)
        user.setdefault("inventory", {})
        return user

    @commands.command()
    async def gift(self, ctx, member: discord.Member = None, *, name: str = None):
        await ctx.send("Gifting is temporarily disabled while we fix saving.")

async def setup(bot):
    await bot.add_cog(Gift(bot))