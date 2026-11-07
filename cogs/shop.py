import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")
        self.late_catches = {}

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
        user.setdefault("coins", 0)
        user.setdefault("inventory", {})
        return user

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(
            title="PokéLarp Shop",
            description="Spend your coins on useful items!",
            color=0xFF69B4
        )
        embed.add_field(
            name="Poké Ball — 50 coins",
            value="Late-catch a Pokémon up to 5 minutes after someone else caught it.\nUse `!buy ball`",
            inline=False
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
        embed.set_footer(text="Earn coins by catching Pokémon!")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item: str = None):
        if not item or item.lower() != "ball":
            await ctx.send("Usage: `!buy ball`")
            return

        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["coins"] < 50:
            await ctx.send(f"You need 50 coins. You have {user['coins']}.")
            return

        user["coins"] -= 50
        user["inventory"]["ball"] = user["inventory"].get("ball", 0) + 1
        self.save_data(data)
        await ctx.send(f"Bought a **Poké Ball**! You now have {user['inventory']['ball']}.")

    @commands.command()
    async def ball(self, ctx):
        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["inventory"].get("ball", 0) < 1:
            await ctx.send("You don't have any Poké Balls. Buy one with `!buy ball`.")
            return

        recent = None
        for cid, info in list(self.late_catches.items()):
            if datetime.utcnow() < info["expires"]:
                recent = info
                break
            else:
                del self.late_catches[cid]

        if not recent:
            await ctx.send("Nothing to late-catch right now.")
            return

        user["inventory"]["ball"] -= 1
        poke = recent["pokemon"]
        user["pokemon"].append({
            "name": poke["name"],
            "dex": poke["dex"],
            "shiny": poke.get("shiny", False),
            "nickname": None,
            "level": 1,
            "caught_at": datetime.utcnow().isoformat()
        })
        if poke["name"] not in user.get("levels", {}):
            user.setdefault("levels", {})[poke["name"]] = 1
        self.save_data(data)
        await ctx.send(f"Used a Poké Ball! You late-caught a **{poke['name']}**!")

    def add_late_catch(self, channel_id, pokemon_data):
        self.late_catches[channel_id] = {
            "pokemon": pokemon_data,
            "expires": datetime.utcnow() + timedelta(minutes=5)
        }

async def setup(bot):
    await bot.add_cog(Shop(bot))