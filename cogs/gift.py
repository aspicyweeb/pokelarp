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
        latest = self.load_data()
        latest["users"].update(data.get("users", {}))
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(latest, f, indent=2)

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
        if not member or not name:
            await ctx.send("Usage: `!gift @user <pokemon>`")
            return

        if member.bot or member == ctx.author:
            await ctx.send("You can't gift to yourself or a bot.")
            return

        data = self.load_data()
        giver = self.ensure_user(data, str(ctx.author.id))
        receiver = self.ensure_user(data, str(member.id))

        if not giver.get("pokemon"):
            await ctx.send("You don't have any Pokémon to gift.")
            return

        target = None
        for i, p in enumerate(giver["pokemon"]):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                target = giver["pokemon"].pop(i)
                break

        if not target:
            await ctx.send(f"You don't have a {name}.")
            return

        receiver["pokemon"].append(target)

        # Move level if it exists
        if target["name"] in giver.get("levels", {}):
            receiver["levels"][target["name"]] = giver["levels"].pop(target["name"])

        self.save_data(data)
        await ctx.send(f"🎁 **{ctx.author.display_name}** gifted **{target['name']}** to **{member.display_name}**!")

async def setup(bot):
    await bot.add_cog(Gift(bot))