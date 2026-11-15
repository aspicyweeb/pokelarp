import asyncio
import io

import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageEnhance

import cogs as storage

_sprite_cache = {}


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
        if not user or not user.get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        caught_dex = {p.get("dex") for p in user["pokemon"] if p.get("dex")}
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
            image = sprite
            if dex not in caught_dex:
                image = ImageEnhance.Color(sprite).enhance(0)
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            panel.paste(image, (x, y), image)

        buf = io.BytesIO()
        panel.save(buf, format="PNG")
        buf.seek(0)

        count = len(caught_dex & set(range(1, total + 1)))
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