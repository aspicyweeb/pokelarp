import discord
from discord.ext import commands
import json
import os
from PIL import Image, ImageEnhance
import aiohttp
import io

class Pokedex(commands.Cog):
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

    async def get_sprite(self, dex, session, grey=False):
        url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex}.png"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                if grey:
                    img = ImageEnhance.Color(img).enhance(0)
                return img
        except:
            return None

    @commands.command(aliases=["dex", "pokedex"])
    async def pokedex(self, ctx):
        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        caught_dex = {p.get("dex") for p in data["users"][user_id]["pokemon"] if p.get("dex")}
        total = 151

        cols = 16
        size = 40
        padding = 2
        rows = (total + cols - 1) // cols
        width = cols * (size + padding) + padding
        height = rows * (size + padding) + padding
        panel = Image.new("RGBA", (width, height), (25, 25, 25, 255))

        async with aiohttp.ClientSession() as session:
            for i in range(1, total + 1):
                row = (i - 1) // cols
                col = (i - 1) % cols
                x = padding + col * (size + padding)
                y = padding + row * (size + padding)

                grey = i not in caught_dex
                sprite = await self.get_sprite(i, session, grey)
                if sprite:
                    sprite = sprite.resize((size, size), Image.Resampling.LANCZOS)
                    panel.paste(sprite, (x, y), sprite)

        buf = io.BytesIO()
        panel.save(buf, format="PNG")
        buf.seek(0)

        count = len(caught_dex)
        percent = round((count / total) * 100, 1)
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Pokédex",
            description=f"**{count}/{total}** caught ({percent}%)",
            color=0xFF69B4
        )
        file = discord.File(buf, filename="pokedex.png")
        embed.set_image(url="attachment://pokedex.png")
        await ctx.send(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Pokedex(bot))
