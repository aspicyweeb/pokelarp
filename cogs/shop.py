import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone

import cogs as storage
from cogs import (
    CHARM_SHINY_CHANCE,
    apply_evolution,
    apply_shiny_charm,
    find_owned,
    get_sprite,
    grant_catch,
    mon_level,
    stone_target,
)

PRICES = {"ball": 50, "greatball": 100, "candy": 75, "stone": 150, "charm": 200}
BALL_WINDOW = timedelta(minutes=5)
GREAT_WINDOW = timedelta(minutes=15)


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="PokéLarp Shop", description="Spend your coins!", color=0xFF69B4)
        embed.add_field(name="Poké Ball — 50", value="`!buy ball`\nlate catch, 5 min", inline=True)
        embed.add_field(name="Great Ball — 100", value="`!buy greatball`\nlate catch, 15 min", inline=True)
        embed.add_field(name="Rare Candy — 75", value="`!buy candy`\n`!candy <pokemon>`", inline=True)
        embed.add_field(name="Evolution Stone — 150", value="`!buy stone`\n`!stone <pokemon>`", inline=True)
        embed.add_field(name="Shiny Charm — 200", value="`!buy charm`\n`!charm` then catch", inline=True)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item: str = None):
        if not item or item.lower() not in PRICES:
            await ctx.send("Usage: `!buy ball|greatball|candy|stone|charm`")
            return
        item = item.lower()
        user = storage.ensure_user(ctx.author.id)
        cost = PRICES[item]
        if user["coins"] < cost:
            await ctx.send(f"Need {cost} coins. You have {user['coins']}.")
            return
        user["coins"] -= cost
        user["inventory"][item] = user["inventory"].get(item, 0) + 1
        storage.save()
        await ctx.send(f"Bought **{item}** for {cost} coins. You have **{user['coins']}** left.")

    def _take_item(self, user, item):
        have = user.get("inventory", {}).get(item, 0)
        if have < 1:
            return False
        user["inventory"][item] = have - 1
        if user["inventory"][item] <= 0:
            user["inventory"].pop(item, None)
        return True

    @commands.command()
    async def candy(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!candy <pokemon>`")
            return
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return
        mon = find_owned(user, name)
        if mon is None:
            await ctx.send(f"You don't have a {name}.")
            return
        if storage.mon_offered(mon):
            await ctx.send("That Pokémon is offered in a trade. `!cancel` the trade first.")
            return
        if not self._take_item(user, "candy"):
            await ctx.send("You don't have a Rare Candy. `!buy candy`")
            return
        level = mon_level(user, mon) + 1
        mon["level"] = level
        user.setdefault("levels", {})[mon["name"]] = max(user["levels"].get(mon["name"], 1), level)
        storage.save()
        await ctx.send(f"**{mon['name']}** grew to level **{level}**!")

    @commands.command()
    async def stone(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!stone <pokemon>`  (Eevee: `!stone eevee vaporeon|jolteon|flareon`)")
            return
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You don't have any Pokémon.")
            return

        mon, new_name, error = stone_target(user, name)
        if error:
            await ctx.send(error)
            return
        if storage.mon_offered(mon):
            await ctx.send("That Pokémon is offered in a trade. `!cancel` the trade first.")
            return

        if not self._take_item(user, "stone"):
            await ctx.send("You don't have an Evolution Stone. `!buy stone`")
            return
        old = apply_evolution(user, mon, new_name)
        storage.save()
        await ctx.send(f"**{old}** evolved into **{new_name}**!")

    @commands.command()
    async def charm(self, ctx):
        user = storage.ensure_user(ctx.author.id)
        if user.get("shiny_charm"):
            await ctx.send("You already have a Shiny Charm active. Catch something first.")
            return
        if not self._take_item(user, "charm"):
            await ctx.send("You don't have a Shiny Charm. `!buy charm`")
            return
        user["shiny_charm"] = True
        storage.save()
        await ctx.send(
            f"Shiny Charm is on. If your next catch isn't already shiny, "
            f"it's {int(CHARM_SHINY_CHANCE * 100)}% to turn shiny. A natural shiny won't use the charm."
        )

    async def _late(self, ctx, window, item, label):
        user = storage.ensure_user(ctx.author.id)
        if not user.get("has_starter", False) and user.get("catches_without_starter", 0) >= 2:
            await ctx.send("Pick a starter with `!starter` before you can catch more.")
            return
        found = storage.get_late_catch(ctx.channel.id)
        if not found:
            parent_id = getattr(ctx.channel, "parent_id", None)
            if parent_id:
                found = storage.get_late_catch(parent_id)
        if not found:
            await ctx.send(f"No recent catch in this channel to use a {label} on.")
            return
        pokemon, at = found
        if datetime.now(timezone.utc) - at > window:
            await ctx.send(f"Too late for a {label}.")
            return
        if not self._take_item(user, item):
            await ctx.send(f"You don't have a {label}. Buy one with `!buy {item}`.")
            return

        shiny = apply_shiny_charm(user, bool(pokemon.get("shiny", False)))

        mon, coins = grant_catch(user, pokemon["name"], pokemon["dex"], shiny)
        storage.save()

        shiny_text = "✨ **SHINY** " if shiny else ""
        embed = discord.Embed(
            description=(
                f"**{ctx.author.display_name}** used a {label} and caught {shiny_text}**{pokemon['name']}**!\n"
                f"+{coins} coins"
            ),
            color=0xFFD700 if shiny else 0xFF69B4,
        )
        embed.set_thumbnail(url=get_sprite(pokemon["dex"], shiny))
        await ctx.send(embed=embed)

    @commands.command()
    async def ball(self, ctx):
        await self._late(ctx, BALL_WINDOW, "ball", "Poké Ball")

    @commands.command()
    async def greatball(self, ctx):
        await self._late(ctx, GREAT_WINDOW, "greatball", "Great Ball")


async def setup(bot):
    await bot.add_cog(Shop(bot))