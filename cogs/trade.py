import discord
from discord.ext import commands
import json
import os

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                data = json.load(f)
                data.setdefault("users", {})
                data.setdefault("trades", {})
                return data
        return {"users": {}, "trades": {}}

    def save_data(self, data):
        # Reload latest so we don't overwrite other changes
        latest = self.load_data()
        latest["users"].update(data.get("users", {}))
        latest["trades"] = data.get("trades", latest.get("trades", {}))
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(latest, f, indent=2)

    @commands.command()
    async def trade(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Usage: `!trade @user`")
            return
        if member.bot or member == ctx.author:
            await ctx.send("You can't trade with yourself or a bot.")
            return

        data = self.load_data()
        trade_id = f"{min(ctx.author.id, member.id)}_{max(ctx.author.id, member.id)}"
        data["trades"][trade_id] = {
            "user1": ctx.author.id,
            "user2": member.id,
            "offer1": None,
            "offer2": None,
            "confirm1": False,
            "confirm2": False
        }
        self.save_data(data)
        await ctx.send(f"Trade started between **{ctx.author.display_name}** and **{member.display_name}**!\n"
                       f"Both use `!offer <pokemon>` then `!confirm`.")

    @commands.command()
    async def offer(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!offer <pokemon>`")
            return

        data = self.load_data()
        user_id = ctx.author.id
        trade = None
        trade_id = None
        for tid, t in data.get("trades", {}).items():
            if user_id in (t["user1"], t["user2"]):
                trade = t
                trade_id = tid
                break

        if not trade:
            await ctx.send("You don't have an active trade. Start one with `!trade @user`.")
            return

        user_data = data["users"].get(str(user_id), {})
        if not user_data.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return

        found = False
        for p in user_data["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                if user_id == trade["user1"]:
                    trade["offer1"] = p["name"]
                else:
                    trade["offer2"] = p["name"]
                found = True
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        self.save_data(data)
        await ctx.send(f"**{ctx.author.display_name}** offered **{name}**.")

        if trade["offer1"] and trade["offer2"]:
            await ctx.send("Both offers are in! Type `!confirm` to finish.")

    @commands.command()
    async def confirm(self, ctx):
        data = self.load_data()
        user_id = ctx.author.id
        trade = None
        trade_id = None
        for tid, t in data.get("trades", {}).items():
            if user_id in (t["user1"], t["user2"]):
                trade = t
                trade_id = tid
                break

        if not trade or not trade.get("offer1") or not trade.get("offer2"):
            await ctx.send("Both people need to `!offer` something first.")
            return

        if user_id == trade["user1"]:
            trade["confirm1"] = True
        else:
            trade["confirm2"] = True

        if trade["confirm1"] and trade["confirm2"]:
            u1 = data["users"].get(str(trade["user1"]), {})
            u2 = data["users"].get(str(trade["user2"]), {})

            def take(user, name):
                for i, p in enumerate(user.get("pokemon", [])):
                    if p["name"] == name:
                        return user["pokemon"].pop(i)
                return None

            p1 = take(u1, trade["offer1"])
            p2 = take(u2, trade["offer2"])

            if p1 and p2:
                u1.setdefault("pokemon", []).append(p2)
                u2.setdefault("pokemon", []).append(p1)
                del data["trades"][trade_id]
                self.save_data(data)
                await ctx.send("Trade complete!")
            else:
                await ctx.send("Something went wrong finding the Pokémon.")
                if trade_id in data["trades"]:
                    del data["trades"][trade_id]
                self.save_data(data)
        else:
            self.save_data(data)
            await ctx.send(f"**{ctx.author.display_name}** confirmed. Waiting for the other person.")

    @commands.command()
    async def cancel(self, ctx):
        data = self.load_data()
        user_id = ctx.author.id
        for tid, t in list(data.get("trades", {}).items()):
            if user_id in (t["user1"], t["user2"]):
                del data["trades"][tid]
                self.save_data(data)
                await ctx.send("Trade cancelled.")
                return
        await ctx.send("You don't have an active trade.")

async def setup(bot):
    await bot.add_cog(Trade(bot))