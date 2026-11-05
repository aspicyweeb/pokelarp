import random
import discord
from discord.ext import commands

class Shiny(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SHINY_CHANCE = 0.01

    def get_sprite(self, dex_num, shiny=False):
        if shiny:
            return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{dex_num}.png"
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

    # This cog expects the main bot to call these helpers
    # or you can move the spawn logic here later

async def setup(bot):
    await bot.add_cog(Shiny(bot))
