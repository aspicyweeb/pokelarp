import discord
from discord.ext import commands

import cogs as storage
from cogs import mon_level


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["me"])
    async def profile(self, ctx):
        user = storage.data.get("users", {}).get(str(ctx.author.id))
        if not user or not user.get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        pokemon = user.get("pokemon", [])
        total = len(pokemon)
        unique = len({p["name"] for p in pokemon})

        starter = "None"
        for mon in pokemon:
            if mon.get("starter"):
                starter = mon["name"]
                break
        else:
            for mon in pokemon:
                if mon.get("name") in ["Bulbasaur", "Charmander", "Squirtle"]:
                    starter = mon["name"]
                    break

        best = max(pokemon, key=lambda mon: mon_level(user, mon))
        highest = f"{best['name']} (Lv.{mon_level(user, best)})"

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Profile", color=0xFF69B4)
        embed.add_field(name="Starter", value=starter, inline=True)
        embed.add_field(name="Total Caught", value=str(total), inline=True)
        embed.add_field(name="Unique", value=f"{unique}/151", inline=True)
        embed.add_field(name="Highest Level", value=highest, inline=True)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))