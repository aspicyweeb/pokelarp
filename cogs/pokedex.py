import asyncio
import io

import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageEnhance

import cogs as storage
from cogs import NAME_TO_DEX, canonical_species, note_dex, remember_species_level

_sprite_cache = {}
_BY_LOWER = {name.lower(): name for name in NAME_TO_DEX}


def species_of(mon):
    raw = mon.get("name") if isinstance(mon, dict) else mon
    if not isinstance(raw, str):
        return None
    if raw in NAME_TO_DEX:
        return raw
    canon = canonical_species(raw)
    if canon:
        return canon
    return _BY_LOWER.get(" ".join(raw.strip().lower().split()))


def register_seen(user):
    """Mark every species they hold or have ever held. A shiny does not replace the regular."""
    if not isinstance(user, dict):
        return set(), False
    before = list(user.get("dex") or [])
    wrote_dex_field = False
    for mon in user.get("pokemon") or []:
        name = species_of(mon)
        number = NAME_TO_DEX.get(name) if name else None
        if number is None and isinstance(mon, dict):
            try:
                raw_dex = int(mon.get("dex"))
            except (TypeError, ValueError):
                raw_dex = None
            if raw_dex and 1 <= raw_dex <= 151:
                number = raw_dex
                name = next((n for n, i in NAME_TO_DEX.items() if i == number), None)
        if not number:
            continue
        note_dex(user, number)
        if name:
            level = 1
            if isinstance(mon, dict) and isinstance(mon.get("level"), int) and mon["level"] >= 1:
                level = mon["level"]
            remember_species_level(user, name, level)
            if isinstance(mon, dict) and mon.get("dex") != number:
                mon["dex"] = number
                wrote_dex_field = True
    for raw_name in list(user.get("levels") or {}):
        canon = species_of(raw_name)
        number = NAME_TO_DEX.get(canon) if canon else None
        if number:
            note_dex(user, number)
    found = set()
    for raw in user.get("dex") or []:
        try:
            number = int(raw)
        except (TypeError, ValueError):
            continue
        if 1 <= number <= 151:
            found.add(number)
    return found, wrote_dex_field or list(user.get("dex") or []) != before


class Pokedex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_sprite(self, dex, session):
        cached = _sprite_cache.get(dex)
        if cached is not None:
            return cached
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex}.png"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                raw = await resp.read()
            img = Image.open(io.BytesIO(raw)).convert("RGBA")
            _sprite_cache[dex] = img
            return img
        except (aiohttp.ClientError, OSError):
            return None

    @commands.command(name="pokedex", aliases=["dex"])
    async def pokedex_cmd(self, ctx):
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        caught_dex, changed = register_seen(user or {})
        if changed:
            storage.save()
        if not caught_dex:
            await ctx.send("You haven't caught any Pokémon yet!")
            return
        total = 151
        cols = 16
        size = 40
        padding = 2
        rows = (total + cols - 1) // cols
        width = cols * (size + padding) + padding
        height = rows * (size + padding) + padding
        panel = Image.new("RGBA", (width, height), (25, 25, 25, 255))

        timeout = aiohttp.ClientTimeout(total=40)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            semaphore = asyncio.Semaphore(20)

            async def one(dex):
                async with semaphore:
                    return dex, await self.get_sprite(dex, session)

            sprites = await asyncio.gather(*(one(i) for i in range(1, total + 1)))

        for dex, sprite in sprites:
            if sprite is None:
                continue
            row = (dex - 1) // cols
            col = (dex - 1) % cols
            x = padding + col * (size + padding)
            y = padding + row * (size + padding)
            image = sprite.copy()
            if dex not in caught_dex:
                image = ImageEnhance.Color(image).enhance(0)
                image = ImageEnhance.Brightness(image).enhance(0.28)
            image = image.resize((size, size), getattr(getattr(Image, "Resampling", Image), "LANCZOS"))
            panel.paste(image, (x, y), image)

        buf = io.BytesIO()
        panel.save(buf, format="PNG")
        buf.seek(0)

        count = len(caught_dex)
        percent = round((count / total) * 100, 1)
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Pokédex",
            description=f"**{count}/{total}** caught ({percent}%)",
            color=0xFF69B4,
        )
        file = discord.File(buf, filename="pokedex.png")
        embed.set_image(url="attachment://pokedex.png")
        await ctx.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(Pokedex(bot))