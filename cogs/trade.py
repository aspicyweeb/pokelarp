import discord
from discord.ext import commands

import cogs as storage
from cogs import find_owned


def _snapshot(mon):
    return {
        "name": mon["name"],
        "dex": mon.get("dex"),
        "shiny": bool(mon.get("shiny", False)),
        "nickname": mon.get("nickname"),
        "level": mon.get("level", 1),
        "caught_at": mon.get("caught_at"),
        "starter": bool(mon.get("starter", False)),
    }


def _same(mon, snap):
    return mon.get("caught_at") == snap.get("caught_at") and mon.get("name") == snap.get("name")


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _open_for(self, user_id):
        user_id = str(user_id)
        for trade_id, trade in storage.data.get("trades", {}).items():
            if user_id in (trade.get("a"), trade.get("b")):
                return trade_id, trade
        return None, None

    @commands.command()
    async def trade(self, ctx, member: discord.Member = None):
        if member is None:
            await ctx.send("Usage: `!trade @user`")
            return
        if member.bot or member.id == ctx.author.id:
            await ctx.send("You can't trade with that user.")
            return
        _, existing = self._open_for(ctx.author.id)
        _, theirs = self._open_for(member.id)
        if existing or theirs:
            await ctx.send("You or they already have an open trade. `!cancel` it first.")
            return

        trade_id = f"{ctx.channel.id}:{ctx.author.id}:{member.id}"
        storage.data.setdefault("trades", {})[trade_id] = {
            "channel_id": ctx.channel.id,
            "a": str(ctx.author.id),
            "b": str(member.id),
            "offer_a": None,
            "offer_b": None,
            "confirm_a": False,
            "confirm_b": False,
        }
        storage.save()
        await ctx.send(
            f"Trade started between **{ctx.author.display_name}** and **{member.display_name}**.\n"
            "Each of you: `!offer <pokemon>`, then `!confirm`."
        )

    def _side(self, trade, user_id):
        user_id = str(user_id)
        if trade["a"] == user_id:
            return "a"
        if trade["b"] == user_id:
            return "b"
        return None

    @commands.command()
    async def offer(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!offer <pokemon>`")
            return
        trade_id, trade = self._open_for(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an open trade. Start one with `!trade @user`.")
            return
        if trade.get("channel_id") != ctx.channel.id:
            await ctx.send("Finish that trade in the channel it was started in.")
            return
        side = self._side(trade, ctx.author.id)
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return
        mon = find_owned(user, name)
        if mon is None:
            await ctx.send(f"You don't have a {name}.")
            return
        trade[f"offer_{side}"] = _snapshot(mon)
        trade["confirm_a"] = False
        trade["confirm_b"] = False
        storage.save()
        shiny = "✨ " if mon.get("shiny") else ""
        await ctx.send(f"**{ctx.author.display_name}** offers {shiny}**{mon['name']}**. Both sides still need `!confirm`.")

    @commands.command()
    async def confirm(self, ctx):
        trade_id, trade = self._open_for(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an open trade.")
            return
        if trade.get("channel_id") != ctx.channel.id:
            await ctx.send("Confirm in the channel the trade was started in.")
            return
        if not trade.get("offer_a") or not trade.get("offer_b"):
            await ctx.send("Both people need to `!offer` something first.")
            return
        side = self._side(trade, ctx.author.id)
        trade[f"confirm_{side}"] = True
        if not (trade.get("confirm_a") and trade.get("confirm_b")):
            storage.save()
            await ctx.send(f"**{ctx.author.display_name}** confirmed. Waiting on the other person.")
            return

        user_a = storage.ensure_user(trade["a"])
        user_b = storage.ensure_user(trade["b"])
        mon_a = storage.pop_pokemon(user_a, lambda mon: _same(mon, trade["offer_a"]))
        mon_b = storage.pop_pokemon(user_b, lambda mon: _same(mon, trade["offer_b"]))
        if mon_a is None or mon_b is None:
            if mon_a is not None:
                user_a["pokemon"].append(mon_a)
            if mon_b is not None:
                user_b["pokemon"].append(mon_b)
            storage.data.get("trades", {}).pop(trade_id, None)
            storage.save()
            await ctx.send("Trade cancelled — one of the offered Pokémon isn't there anymore.")
            return
        user_a["pokemon"].append(mon_b)
        user_b["pokemon"].append(mon_a)
        storage.data.get("trades", {}).pop(trade_id, None)
        storage.save()
        await ctx.send(
            f"Trade complete. **{trade['offer_a']['name']}** ↔ **{trade['offer_b']['name']}**."
        )

    @commands.command()
    async def cancel(self, ctx):
        trade_id, trade = self._open_for(ctx.author.id)
        if trade is None:
            await ctx.send("You don't have an open trade.")
            return
        storage.data.get("trades", {}).pop(trade_id, None)
        storage.save()
        await ctx.send("Trade cancelled.")


async def setup(bot):
    await bot.add_cog(Trade(bot))