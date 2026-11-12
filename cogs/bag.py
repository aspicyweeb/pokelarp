import discord
from discord.ext import commands

import cogs as storage
from cogs import TYPES, find_owned, get_sprite, mon_level


def chunk_lines(lines, limit=3500):
    if not lines:
        return [""]
    blocks = []
    current = ""
    for line in lines:
        extra = line if not current else "\n" + line
        if current and len(current) + len(extra) > limit:
            blocks.append(current)
            current = line
        else:
            current += extra
    if current:
        blocks.append(current)
    return blocks


class Bag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _group(self, user, pokemon):
        groups = {}
        order = []
        for mon in pokemon:
            key = mon["name"]
            if key not in groups:
                groups[key] = {"count": 0, "shiny": 0, "level": 1, "nick": None}
                order.append(key)
            group = groups[key]
            group["count"] += 1
            if mon.get("shiny"):
                group["shiny"] += 1
            group["level"] = max(group["level"], mon_level(user, mon))
            if mon.get("nickname") and not group["nick"]:
                group["nick"] = mon["nickname"]
        return groups, order

    def _format(self, name, group):
        shiny = "✨ " if group["shiny"] else ""
        nick = f" ({group['nick']})" if group["nick"] else ""
        count = f" ×{group['count']}" if group["count"] > 1 else ""
        return f"{shiny}**{name}**{nick}{count} — Lv.{group['level']}"

    @commands.command()
    async def bag(self, ctx, filter: str = None):
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        pokemon = user.get("pokemon", [])
        coins = user.get("coins", 0)
        balls = user.get("inventory", {}).get("ball", 0)
        footer = f"\n\n**Coins:** {coins}\n**Poké Balls:** {balls}"

        if not filter or filter.lower() in ["all", "pokemon", "pkmn"]:
            groups, order = self._group(user, pokemon)
            lines = [self._format(name, groups[name]) for name in order]
            title = f"{ctx.author.display_name}'s Pokémon"
            pages = chunk_lines(lines)
            pages[-1] += footer
        elif filter.lower() in ["shiny", "shinies", "sparkle"]:
            lines = []
            for mon in pokemon:
                if not mon.get("shiny"):
                    continue
                level = mon_level(user, mon)
                nick = f" ({mon['nickname']})" if mon.get("nickname") else ""
                lines.append(f"✨ **{mon['name']}**{nick} — Lv.{level}")
            title = f"{ctx.author.display_name}'s Shinies"
            pages = chunk_lines(lines) if lines else ["No shinies yet!"]
        elif filter.lower() in ["items", "shop", "inv", "inventory"]:
            inventory = user.get("inventory", {})
            title = f"{ctx.author.display_name}'s Items"
            if inventory:
                lines = [f"**{name}** ×{qty}" for name, qty in sorted(inventory.items()) if qty]
                body = "\n".join(lines) if lines else "No items."
            else:
                body = "No items."
            pages = [f"{body}\n\n**Coins:** {coins}"]
        else:
            type_names = {t.lower() for types in TYPES.values() for t in types}
            if filter.lower() not in type_names:
                await ctx.send("Usage: `!bag` | `!bag shinies` | `!bag items` | `!bag Fire`")
                return
            target_type = filter.capitalize()
            lines = []
            groups, order = self._group(user, pokemon)
            for name in order:
                if target_type in TYPES.get(name, []):
                    lines.append(self._format(name, groups[name]))
            title = f"{ctx.author.display_name}'s {target_type} Types"
            pages = chunk_lines(lines) if lines else [f"No {target_type} types yet!"]

        for index, page in enumerate(pages):
            page_title = title if index == 0 else f"{title} ({index + 1}/{len(pages)})"
            embed = discord.Embed(title=page_title, description=page or "None", color=0xFF69B4)
            await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!info <pokemon>`")
            return
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user:
            await ctx.send("You don't have any Pokémon yet.")
            return
        found = find_owned(user, name)
        if found is None:
            await ctx.send(f"You don't have a {name}.")
            return

        level = mon_level(user, found)
        shiny = found.get("shiny", False)
        nick = found.get("nickname")
        display = nick if nick else found["name"]
        types = ", ".join(TYPES.get(found["name"], ["???"]))
        owned = sum(1 for mon in user.get("pokemon", []) if mon["name"] == found["name"])

        embed = discord.Embed(
            title=f"{'✨ ' if shiny else ''}{display}",
            description=(
                f"**{found['name']}** — Level {level}\n"
                f"Dex #{found.get('dex', '?')}\n"
                f"Type: {types}\n"
                f"You own {owned}"
            ),
            color=0xFFD700 if shiny else 0xFF69B4,
        )
        if found.get("dex"):
            embed.set_image(url=get_sprite(found["dex"], shiny))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bag(bot))