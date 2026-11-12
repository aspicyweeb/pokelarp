from discord.ext import commands

import cogs as storage


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spawnrate(self, ctx, min_minutes: int = None, max_minutes: int = None):
        channel_id = ctx.channel.id
        rates = storage.spawn_channel_map()
        current = rates.get(channel_id)

        if min_minutes is None and max_minutes is None:
            if current:
                await ctx.send(
                    f"This channel spawns every **{current['min']}–{current['max']}** minutes "
                    "(the wait is picked once per spawn, not rerolled).\n"
                    "Usage: `!spawnrate <min> <max>` or `!spawnrate off`"
                )
            else:
                await ctx.send(
                    "This channel is not a spawn channel.\n"
                    "Usage: `!spawnrate <min> <max>` to make it one, or `!spawnrate off` to remove it."
                )
            return

        if max_minutes is None:
            await ctx.send("Usage: `!spawnrate <min> <max>` or `!spawnrate off`")
            return
        if min_minutes < 1 or max_minutes < min_minutes:
            await ctx.send("Min must be at least 1 and max must be at least min.")
            return
        if max_minutes > 24 * 60:
            await ctx.send("Max can't be more than a day.")
            return

        storage.set_spawn_rate(channel_id, min_minutes, max_minutes)
        await ctx.send(
            f"Spawn rate here is now **{min_minutes}–{max_minutes}** minutes. "
            "It starts after the next spawn."
        )

    @spawnrate.error
    async def spawnrate_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Only admins can change the spawn rate.")
            return
        if isinstance(error, commands.BadArgument):
            # Lets `!spawnrate off` work without a converter fight.
            if ctx.message.content.lower().strip().endswith(" off"):
                storage.remove_spawn_channel(ctx.channel.id)
                await ctx.send("This channel will no longer spawn Pokémon.")
                return
            await ctx.send("Usage: `!spawnrate <min> <max>` or `!spawnrate off`")
            return
        raise error


async def setup(bot):
    await bot.add_cog(Admin(bot))