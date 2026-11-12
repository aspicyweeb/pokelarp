import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="commands", description="Show all PokéLarp commands")
    async def commands_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(title="PokéLarp Commands", color=0xFF69B4)
        embed.add_field(
            name="Catching",
            value=(
                "`catch` — catch the wild Pokémon in this channel\n"
                "`!starter` — pick your starter (once)\n"
                "`!ball` — copy of the last catch here, within 5 min\n"
                "`!greatball` — same, within 15 min"
            ),
            inline=False,
        )
        embed.add_field(
            name="Your Pokémon",
            value=(
                "`!bag` — see your Pokémon + coins\n"
                "`!bag shinies` / `!bag Fire` — filters\n"
                "`!info <name>` — details on one\n"
                "`!nickname <pokemon> <name>` — rename\n"
                "`!release <pokemon>` — remove one\n"
                "`!dex` — Pokédex progress\n"
                "`!evolve <pokemon>` — free evolve, once a day (first stage)"
            ),
            inline=False,
        )
        embed.add_field(
            name="Daily",
            value="`!daily` — claim 25 coins (every 24h)",
            inline=False,
        )
        embed.add_field(
            name="Shop",
            value=(
                "`!shop` — see items\n"
                "`!buy ball|greatball|candy|stone|charm`\n"
                "`!candy <pokemon>` — level up one\n"
                "`!stone <pokemon>` — evolve, including second stage\n"
                "`!charm` — next catch has a 5% shiny chance"
            ),
            inline=False,
        )
        embed.add_field(
            name="Social",
            value=(
                "`!gift @user <pokemon>` — give a Pokémon\n"
                "`!trade @user` — start a trade, then `!offer` / `!confirm`\n"
                "`!me` — your profile\n"
                "`!leaderboard` — top catchers"
            ),
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))