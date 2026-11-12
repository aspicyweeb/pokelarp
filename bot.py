"""Pokelarp — a Gen 1 Discord catch bot.

    DISCORD_TOKEN=... DATA_PATH=/data/pokelarp_data.json python bot.py

Turn on the Message Content intent in the Discord developer portal or `catch`
and the other prefix commands never fire.
"""
import os
import random
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

import discord
from discord.ext import commands, tasks

import cogs as storage
from cogs import (
    CHARM_SHINY_CHANCE,
    EVO_MAP,
    SHINY_CHANCE,
    STARTERS,
    apply_evolution,
    find_owned,
    get_sprite,
    get_weighted_pokemon,
    grant_catch,
    new_mon,
    remember_species_level,
)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

_missing_channels = set()
_booted = False


async def announce_spawn(channel, spawn):
    name = spawn["name"]
    shiny = spawn.get("shiny", False)
    title = f"✨ A wild shiny {name} appeared!" if shiny else f"A wild {name} appeared!"
    embed = discord.Embed(
        title=title,
        description="Type **catch** to catch it!",
        color=0xFFD700 if shiny else 0xFF69B4,
    )
    embed.set_image(url=spawn["sprite"])
    embed.set_footer(text="Pokelarp • Gen 1" + (" • SHINY" if shiny else ""))
    await channel.send(embed=embed)


def create_spawn(channel_id, now=None):
    now = now or datetime.now(timezone.utc)
    dex, name = get_weighted_pokemon()
    shiny = random.random() < SHINY_CHANCE
    spawn = {
        "name": name,
        "dex": dex,
        "sprite": get_sprite(dex, shiny),
        "shiny": shiny,
        "spawned_at": now.isoformat(),
        "channel_id": channel_id,
    }
    storage.data.setdefault("spawns", {})[str(channel_id)] = spawn
    rates = storage.spawn_channel_map().get(channel_id)
    if rates:
        wait = random.randint(rates["min"], rates["max"])
        storage.schedule_next_spawn(channel_id, now + timedelta(minutes=wait))
    storage.save()
    return spawn


async def load_cogs():
    cog_dir = Path(__file__).resolve().parent / "cogs"
    for filename in sorted(os.listdir(cog_dir)):
        if filename.endswith(".py") and filename != "__init__.py":
            ext = f"cogs.{filename[:-3]}"
            if ext in bot.extensions:
                continue
            try:
                await bot.load_extension(ext)
                print(f"Loaded cog: {filename}")
            except Exception as exc:
                print(f"Failed to load {filename}: {exc}")


@bot.event
async def on_ready():
    global _booted
    print(f"Pokelarp is online as {bot.user}")
    await load_cogs()
    if not _booted:
        _booted = True
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} slash commands")
        except Exception as exc:
            print(f"Failed to sync slash commands: {exc}")
        for channel_id, spawn in list(storage.data.get("spawns", {}).items()):
            channel = bot.get_channel(int(channel_id))
            if channel is None:
                continue
            try:
                await announce_spawn(channel, spawn)
            except discord.HTTPException as exc:
                print(f"Could not reannounce spawn in {channel_id}: {exc}")
    if not spawn_loop.is_running():
        spawn_loop.start()


@tasks.loop(minutes=1)
async def spawn_loop():
    try:
        await spawn_due_channels()
    except Exception:
        traceback.print_exc()


async def spawn_due_channels():
    now = datetime.now(timezone.utc)
    spawns = storage.data.setdefault("spawns", {})
    for channel_id, _rates in storage.spawn_channel_map().items():
        if str(channel_id) in spawns:
            continue
        nxt = storage.next_spawn_at(channel_id)
        if nxt is not None and now < nxt:
            continue
        channel = bot.get_channel(channel_id)
        if channel is None:
            if channel_id not in _missing_channels:
                print(f"Spawn channel {channel_id} is not visible to the bot. Check the id and permissions.")
                _missing_channels.add(channel_id)
            continue
        spawn = create_spawn(channel_id, now)
        try:
            await announce_spawn(channel, spawn)
        except discord.HTTPException as exc:
            print(f"Failed to announce in {channel_id}: {exc}")
            spawns.pop(str(channel_id), None)
            storage.data.get("next_spawn", {}).pop(str(channel_id), None)
            storage.save()


async def handle_catch(message, spawn):
    user = storage.ensure_user(message.author.id)
    if not user.get("has_starter", False) and user.get("catches_without_starter", 0) >= 2:
        await message.channel.send(
            f"**{message.author.display_name}**, you need to pick a starter first!\n"
            "Use `!starter` to choose Bulbasaur, Charmander, or Squirtle before catching more."
        )
        return

    name = spawn["name"]
    dex = spawn["dex"]
    shiny = bool(spawn.get("shiny", False))
    if user.get("shiny_charm"):
        if not shiny and random.random() < CHARM_SHINY_CHANCE:
            shiny = True
        user["shiny_charm"] = False

    spawned_at = storage.parse_dt(spawn.get("spawned_at", datetime.now(timezone.utc).isoformat()))
    catch_time = datetime.now(timezone.utc)
    seconds = max(0, (catch_time - spawned_at).total_seconds())
    mins = int(seconds // 60)
    secs = round(seconds % 60, 1)

    storage.data.get("spawns", {}).pop(str(message.channel.id), None)
    mon, coins = grant_catch(user, name, dex, shiny)
    storage.set_late_catch(message.channel.id, {"name": name, "dex": dex, "shiny": shiny}, catch_time)
    storage.save()

    count = sum(1 for p in user["pokemon"] if p["name"] == name)
    shiny_text = "✨ **SHINY** " if shiny else ""
    time_text = f"{mins} minute{'s' if mins != 1 else ''} {secs} seconds" if mins else f"{secs} seconds"
    desc = (
        f"**{message.author.display_name}** caught {shiny_text}**{name}**!!!!1!\n"
        f"You now have **{count}** of that type!!!\n"
        f"this cutie was caught in {time_text}!!!!\n"
        f"+{coins} coins"
    )
    if not user.get("has_starter", False):
        remaining = 2 - user["catches_without_starter"]
        if remaining > 0:
            desc += f"\n\nYou still need to pick a starter with `!starter` ({remaining} free catch left)."
        else:
            desc += "\n\nThat's your last free catch! Use `!starter` before you can catch more."

    embed = discord.Embed(description=desc, color=0xFFD700 if shiny else 0xFF69B4)
    embed.set_thumbnail(url=get_sprite(dex, shiny))
    await message.channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.lower().strip()
    if content == "catch":
        try:
            spawns = storage.data.get("spawns", {})
            spawn = spawns.get(str(message.channel.id))
            if spawn:
                await handle_catch(message, spawn)
            elif spawns:
                await message.channel.send("Nothing wild is up in this channel.")
        except Exception:
            traceback.print_exc()
            await message.channel.send("Catch failed. Try again.")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that.")
        return
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Couldn't find that member. Mention them.")
        return
    if isinstance(error, commands.UserInputError):
        await ctx.send("Couldn't read that. Check `/commands` for the usage.")
        return
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    traceback.print_exception(type(error), error, error.__traceback__)
    await ctx.send("Something broke on that command. Try again in a second.")


@bot.command()
async def starter(ctx):
    user = storage.ensure_user(ctx.author.id)
    if user.get("has_starter", False):
        await ctx.send("You already picked a starter!")
        return

    embed = discord.Embed(
        title="Choose your starter!",
        description="Reply with **1**, **2**, or **3**",
        color=0xFF69B4,
    )
    embed.add_field(name="1. Bulbasaur", value="🌱 Grass type", inline=False)
    embed.add_field(name="2. Charmander", value="🔥 Fire type", inline=False)
    embed.add_field(name="3. Squirtle", value="💧 Water type", inline=False)
    embed.set_footer(text="You can only pick once!")
    await ctx.send(embed=embed)

    def check(reply):
        return reply.author == ctx.author and reply.channel == ctx.channel and reply.content in ["1", "2", "3"]

    try:
        reply = await bot.wait_for("message", check=check, timeout=60)
    except TimeoutError:
        await ctx.send("Took too long! Try `!starter` again.")
        return

    choice = STARTERS[reply.content]
    name = choice["name"]
    dex = choice["dex"]
    user["pokemon"].append(new_mon(name, dex, False, starter=True))
    remember_species_level(user, name, 1)
    user["has_starter"] = True
    storage.save()

    embed = discord.Embed(
        title=f"You chose {name}!",
        description=f"**{ctx.author.display_name}** got a level 1 **{name}** as their starter!",
        color=0xFF69B4,
    )
    embed.set_image(url=get_sprite(dex))
    await ctx.send(embed=embed)


@bot.command()
async def spawn(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Only admins can force a spawn.")
        return
    if str(ctx.channel.id) in storage.data.get("spawns", {}):
        await ctx.send("There's already a Pokémon spawned in this channel!")
        return
    created = create_spawn(ctx.channel.id)
    await announce_spawn(ctx.channel, created)


@bot.command()
async def balance(ctx):
    user = storage.data.get("users", {}).get(str(ctx.author.id), {})
    await ctx.send(f"You have **{user.get('coins', 0)}** coins.")


@bot.command()
async def give(ctx, amount: int = None, item: str = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Admins only.")
        return
    if amount is None:
        await ctx.send("Usage: `!give 500` or `!give 5 stone`")
        return
    if amount < 1:
        await ctx.send("Amount has to be at least 1.")
        return

    user = storage.ensure_user(ctx.author.id)
    if item:
        item = item.lower()
        user["inventory"][item] = user["inventory"].get(item, 0) + amount
        storage.save()
        await ctx.send(f"Gave yourself **{amount} {item}**(s).")
    else:
        user["coins"] += amount
        storage.save()
        await ctx.send(f"Gave yourself **{amount}** coins. Balance: {user['coins']}.")


@bot.command()
async def daily(ctx):
    user = storage.ensure_user(ctx.author.id)
    wait = storage.cooldown_remaining(user.get("last_daily"), 24)
    if wait is not None:
        await ctx.send(f"Already claimed. Try again in {storage.format_wait(wait)}.")
        return
    user["coins"] += 25
    user["last_daily"] = datetime.now(timezone.utc).isoformat()
    storage.save()
    await ctx.send(f"+25 coins! You now have **{user['coins']}**.")


@bot.command()
async def evolve(ctx, *, name: str = None):
    if not name:
        await ctx.send("Usage: `!evolve <pokemon>`")
        return
    user = storage.data.get("users", {}).get(str(ctx.author.id))
    if not user or not user.get("pokemon"):
        await ctx.send("You don't have any Pokémon.")
        return

    target = find_owned(user, name)
    if not target or target["name"] not in EVO_MAP:
        await ctx.send("That Pokémon can't be evolved with !evolve. Second stages need `!stone`.")
        return

    wait = storage.cooldown_remaining(user.get("last_evolve"), 24)
    if wait is not None:
        await ctx.send(f"Already used evolve. Try again in {storage.format_wait(wait)}.")
        return

    old = apply_evolution(user, target, EVO_MAP[target["name"]])
    user["last_evolve"] = datetime.now(timezone.utc).isoformat()
    storage.save()
    await ctx.send(f"**{old}** evolved into **{target['name']}**!")


@bot.command()
async def checkdaily(ctx, member: discord.Member = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Admins only.")
        return
    target = member or ctx.author
    user = storage.data.get("users", {}).get(str(target.id), {})
    await ctx.send(
        f"**{target.display_name}**\n"
        f"Last daily: `{user.get('last_daily', 'never')}`\n"
        f"Last evolve: `{user.get('last_evolve', 'never')}`\n"
        f"Coins: {user.get('coins', 0)}"
    )


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_TOKEN is not set.")
    storage.load()
    bot.run(TOKEN)