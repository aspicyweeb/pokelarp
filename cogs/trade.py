import discord
from discord.ext import commands
import json
import os

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")
        self.active_trades = {}  # {user_id: {"partner": id, "offer": pokemon_name}}

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
    async def trade(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Usage: `!trade @user`")
            return
        if member.bot or member == ctx.author:
            await ctx.send("You can't trade with yourself or a bot.")
            return

        self.active_trades[ctx.author.id] = {"partner": member.id, "offer": None}
        self.active_trades[member.id] = {"partner": ctx.author.id, "offer": None}

        await ctx.send(f"Trade started between **{ctx.author.display_name}** and **{member.display_name}**!\n"
                       f"Both of you use `!offer <pokemon>` to choose what you're trading.")

    @commands.command()
    async def offer(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!offer <pokemon>`")
            return

        if ctx.author.id not in self.active_trades:
            await ctx.send("You don't have an active trade. Start one with `!trade @user`.")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return

        user = data["users"][user_id]
        found = False
        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                self.active_trades[ctx.author.id]["offer"] = p["name"]
                found = True
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        partner_id = self.active_trades[ctx.author.id]["partner"]
        await ctx.send(f"**{ctx.author.display_name}** offered **{name}**.")

        # Check if both have offered
        if (partner_id in self.active_trades and 
            self.active_trades[partner_id]["offer"] and 
            self.active_trades[ctx.author.id]["offer"]):
            await ctx.send("Both offers are in! Both of you type `!confirm` to finish the trade.")

    @commands.command()
    async def confirm(self, ctx):
        if ctx.author.id not in self.active_trades:
            await ctx.send("You don't have an active trade.")
            return

        trade = self.active_trades[ctx.author.id]
        partner_id = trade["partner"]
        if partner_id not in self.active_trades or not trade["offer"] or not self.active_trades[partner_id]["offer"]:
            await ctx.send("Both people need to `!offer` something first.")
            return

        # Mark as confirmed
        trade["confirmed"] = True
        if self.active_trades[partner_id].get("confirmed"):
            # Both confirmed — do the swap
            data = self.load_data()
            user1 = data["users"][str(ctx.author.id)]
            user2 = data["users"][str(partner_id)]

            offer1 = trade["offer"]
            offer2 = self.active_trades[partner_id]["offer"]

            # Remove from each and add to the other
            def take(user, name):
                for i, p in enumerate(user["pokemon"]):
                    if p["name"] == name:
                        return user["pokemon"].pop(i)
                return None

            p1 = take(user1, offer1)
            p2 = take(user2, offer2)

            if p1 and p2:
                user1["pokemon"].append(p2)
                user2["pokemon"].append(p1)
                self.save_data(data)
                await ctx.send(f"Trade complete! **{ctx.author.display_name}** got **{offer2}**, partner got **{offer1}**.")
            else:
                await ctx.send("Something went wrong with the trade.")

            # Clear trades
            del self.active_trades[ctx.author.id]
            del self.active_trades[partner_id]
        else:
            await ctx.send(f"**{ctx.author.display_name}** confirmed. Waiting for the other person.")

    @commands.command()
    async def cancel(self, ctx):
        if ctx.author.id in self.active_trades:
            partner_id = self.active_trades[ctx.author.id]["partner"]
            del self.active_trades[ctx.author.id]
            if partner_id in self.active_trades:
                del self.active_trades[partner_id]
            await ctx.send("Trade cancelled.")
        else:
            await ctx.send("You don't have an active trade.")

async def setup(bot):
    await bot.add_cog(Trade(bot))