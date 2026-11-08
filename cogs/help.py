import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="commands", description="Show all PokéLarp commands")
    async def commands_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="PokéLarp Commands",
            color=0xFF69B4
        )
        embed.add_field(name="Catching", value=(
            "`catch` — catch the wild Pokémon\n"
            "`!starter` — pick your starter (once)"
        ), inline=False)
        embed.add_field(name="Your Pokémon", value=(
            "`!bag` — see your Pokémon + coins\n"
            "`!bag shinies` / `!bag Fire` — filters\n"
            "`!info <name>` — details on one\n"
            "`!nickname <pokemon> <name>` — rename\n"
            "`!release <pokemon>` — remove one\n"
            "`!dex` — Pokédex progress"
        ), inline=False)
        embed.add_field(name="Daily", value=(
            "`!daily` — claim 25 coins\n"
            "`!daily <common>` — 25 coins + free evolve"
        ), inline=False)
        embed.add_field(name="Shop", value=(
            "`!shop` — see items\n"
            "`!buy ball` — buy a Poké Ball (50 coins)\n"
            "`!ball` — late catch (5 min)"
        ), inline=False)
        embed.add_field(name="Social", value=(
            "`!gift @user <pokemon>` — give a Pokémon\n"
            "`!trade @user` — start a trade\n"
            "`!me` — your profile\n"
            "`!leaderboard` — top catchers"
        ), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))