import discord
from discord.ext import commands

class DismissView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=120)
        self.author_id = author_id

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your message.", ephemeral=True)
            return
        await interaction.message.delete()

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["commands", "help"])
    async def cmds(self, ctx):
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
            "`!info <name>` — details on one\n"
            "`!nickname <pokemon> <name>` — rename\n"
            "`!release <pokemon>` — remove one\n"
            "`!dex` — Pokédex progress"
        ), inline=False)
        embed.add_field(name="Training", value=(
            "`!grind <pokemon>` — train one\n"
            "`!xp` — check progress\n"
            "`!daily` — coin bonus (+ optional evolve)"
        ), inline=False)
        embed.add_field(name="Shop", value=(
            "`!shop` — see items\n"
            "`!buy ball` — buy a Poké Ball\n"
            "`!ball` — late catch (5 min)"
        ), inline=False)
        embed.add_field(name="Social", value=(
            "`!gift @user <pokemon>` — give a Pokémon\n"
            "`!trade @user` — start a trade\n"
            "`!profile` — your profile\n"
            "`!leaderboard` — top catchers"
        ), inline=False)
        embed.set_footer(text="Click Dismiss to remove this")

        view = DismissView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))