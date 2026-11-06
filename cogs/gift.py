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
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)

    @commands.command()
    async def gift(self, ctx, member: discord.Member = None, *, name: str = None):
        if not member or not name:
            await ctx.send("Usage: `!gift @user <pokemon>`")
            return

        if member.bot or member == ctx.author:
            await ctx.send("You can't gift to yourself or a bot.")
            return

        data = self.load_data()
        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)

        if giver_id not in data["users"] or not data["users"][giver_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon to gift.")
            return

        giver = data["users"][giver_id]
        target = None
        for i, p in enumerate(giver["pokemon"]):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                target = giver["pokemon"].pop(i)
                break

        if not target:
            await ctx.send(f"You don't have a {name}.")
            return

        # Make sure receiver exists
        if receiver_id not in data["users"]:
            data["users"][receiver_id] = {
                "pokemon": [],
                "levels": {},
                "has_starter": False,
                "catches_without_starter": 0
            }

        receiver = data["users"][receiver_id]
        receiver["pokemon"].append(target)

        # Move level if it exists
        if target["name"] in giver.get("levels", {}):
            receiver.setdefault("levels", {})
            receiver["levels"][target["name"]] = giver["levels"].pop(target["name"])

        self.save_data(data)
        await ctx.send(f"🎁 **{ctx.author.display_name}** gifted **{target['name']}** to **{member.display_name}**!")

async def setup(bot):
    await bot.add_cog(Gift(bot))