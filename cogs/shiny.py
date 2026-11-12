from discord.ext import commands

# Shiny rolls live in bot.py (spawn + charm). This cog stays so older
# setups that expect it to load don't error.


class Shiny(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Shiny(bot))
