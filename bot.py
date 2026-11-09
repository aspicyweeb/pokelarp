import os
import discord
from discord.ext import commands, tasks
import random
import json
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
DATA_PATH = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SPAWN_CHANNELS = {
    1568206877286735872: {"min": 5, "max": 45},
    1540133768730509352: {"min": 30, "max": 120},
}

SHINY_CHANCE = 0.01
CHARM_SHINY_CHANCE = 0.05

POKEMON = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot",
    "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok",
    "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina",
    "Nidoqueen", "Nidoran♂", "Nidorino", "Nidoking", "Clefairy", "Clefable",
    "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff", "Zubat", "Golbat",
    "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat",
    "Venomoth", "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck",
    "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine", "Poliwag",
    "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash",
    "Slowpoke", "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo",
    "Dodrio", "Seel", "Dewgong", "Grimer", "Muk", "Shellder",
    "Cloyster", "Gastly", "Haunter", "Gengar", "Onix", "Drowzee",
    "Hypno", "Krabby", "Kingler", "Voltorb", "Electrode", "Exeggcute",
    "Exeggutor", "Cubone", "Marowak", "Hitmonlee", "Hitmonchan", "Lickitung",
    "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey", "Tangela",
    "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu",
    "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar",
    "Pinsir", "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto",
    "Eevee", "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte",
    "Omastar", "Kabuto", "Kabutops", "Aerodactyl", "Snorlax", "Articuno",
    "Zapdos", "Moltres", "Dratini", "Dragonair", "Dragonite", "Mewtwo", "Mew"
]

RARITY = {
    "default": 100,
    "Pikachu": 40, "Eevee": 40, "Growlithe": 40, "Vulpix": 40,
    "Abra": 35, "Machop": 35, "Gastly": 35,
    "Dratini": 15, "Lapras": 15, "Snorlax": 10,
    "Articuno": 3, "Zapdos": 3, "Moltres": 3, "Mewtwo": 2, "Mew": 1,
}

RARE_POKEMON = {"Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Dratini", "Lapras", "Snorlax"}

EVO_MAP = {
    "Pidgey": "Pidgeotto", "Rattata": "Raticate", "Caterpie": "Metapod", "Weedle": "Kakuna",
    "Oddish": "Gloom", "Poliwag": "Poliwhirl", "Abra": "Kadabra", "Machop": "Machoke",
    "Bellsprout": "Weepinbell", "Geodude": "Graveler", "Gastly": "Haunter", "Magikarp": "Gyarados",
    "Spearow": "Fearow", "Ekans": "Arbok", "Sandshrew": "Sandslash", "Zubat": "Golbat",
    "Paras": "Parasect", "Venonat": "Venomoth", "Diglett": "Dugtrio", "Meowth": "Persian",
    "Psyduck": "Golduck", "Mankey": "Primeape", "Growlithe": "Arcanine", "Tentacool": "Tentacruel",
    "Ponyta": "Rapidash", "Slowpoke": "Slowbro", "Magnemite": "Magneton", "Doduo": "Dodrio",
    "Seel": "Dewgong", "Grimer": "Muk", "Shellder": "Cloyster", "Drowzee": "Hypno",
    "Krabby": "Kingler", "Voltorb": "Electrode", "Exeggcute": "Exeggutor", "Cubone": "Marowak",
    "Koffing": "Weezing", "Rhyhorn": "Rhydon", "Horsea": "Seadra", "Goldeen": "Seaking",
    "Staryu": "Starmie", "Dratini": "Dragonair"
}

STARTERS = {
    "1": {"name": "Bulbasaur", "dex": 1},
    "2": {"name": "Charmander", "dex": 4},
    "3": {"name": "Squirtle", "dex": 7}
}

def get_weighted_pokemon():
    weights = [RARITY.get(name, RARITY["default"]) for name in POKEMON]
    dex = random.choices(range(1, 152), weights=weights, k=1)[0]
    return dex, POKEMON[dex - 1]

def get_sprite(dex_num, shiny=False):
    if shiny:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{dex_num}.png"
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

def load_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            data.setdefault("users", {})
            data.setdefault("current_spawn", None)
            return data
    return {"users": {}, "current_spawn": None}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
current_spawn = data.get("current_spawn")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

@bot.event
async def on_ready():
    print(f"Pokelarp is online as {bot.user}")
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")
    spawn_loop.start()

@tasks.loop(minutes=1)
async def spawn_loop():
    global current_spawn
    if current_spawn:
        return

    now = datetime.utcnow()

    for channel_id, rates in SPAWN_CHANNELS.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        channel_last = data.get(f"last_spawn_{channel_id}")
        if channel_last:
            last_dt = datetime.fromisoformat(channel_last)
            wait = timedelta(minutes=random.randint(rates["min"], rates["max"]))
            if now < last_dt + wait:
                continue

        dex, name = get_weighted_pokemon()
        shiny = random.random() < SHINY_CHANCE
        sprite = get_sprite(dex, shiny)

        current_spawn = {
            "name": name,
            "dex": dex,
            "sprite": sprite,
            "shiny": shiny,
            "spawned_at": now.isoformat(),
            "channel_id": channel_id
        }
        data["current_spawn"] = current_spawn
        data[f"last_spawn_{channel_id}"] = now.isoformat()
        save_data(data)

        title = f"✨ A wild shiny {name} appeared!" if shiny else f"A wild {name} appeared!"
        embed = discord.Embed(
            title=title,
            description="Type **catch** to catch it!",
            color=0xFFD700 if shiny else 0xFF69B4
        )
        embed.set_image(url=sprite)
        embed.set_footer(text="Pokelarp • Gen 1" + (" • SHINY" if shiny else ""))
        await channel.send(embed=embed)
        break

@bot.event
async def on_message(message):
    global current_spawn
    if message.author.bot:
        return

    content = message.content.lower().strip()

    if content == "catch" and current_spawn:
        user_id = str(message.author.id)
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "pokemon": [],
                "levels": {},
                "has_starter": False,
                "catches_without_starter": 0,
                "coins": 0,
                "inventory": {}
            }

        user = data["users"][user_id]
        user.setdefault("coins", 0)
        user.setdefault("inventory", {})

        if not user.get("has_starter", False) and user.get("catches_without_starter", 0) >= 2:
            await message.channel.send(
                f"**{message.author.display_name}**, you need to pick a starter first!\n"
                f"Use `!starter` to choose Bulbasaur, Charmander, or Squirtle before catching more."
            )
            return

        name = current_spawn["name"]
        dex = current_spawn["dex"]
        shiny = current_spawn.get("shiny", False)

        if user.get("shiny_charm"):
            if random.random() < CHARM_SHINY_CHANCE:
                shiny = True
            user["shiny_charm"] = False

        sprite = get_sprite(dex, shiny)
        spawned_at = datetime.fromisoformat(current_spawn.get("spawned_at", datetime.utcnow().isoformat()))
        catch_time = datetime.utcnow()
        seconds = (catch_time - spawned_at).total_seconds()
        mins = int(seconds // 60)
        secs = round(seconds % 60, 1)

        user["pokemon"].append({
            "name": name,
            "dex": dex,
            "caught_at": catch_time.isoformat(),
            "level": 1,
            "shiny": shiny,
            "nickname": None
        })

        if name not in user.get("levels", {}):
            user.setdefault("levels", {})[name] = 1

        count = sum(1 for p in user["pokemon"] if p["name"] == name)

        if not user.get("has_starter", False):
            user["catches_without_starter"] = user.get("catches_without_starter", 0) + 1

        coins = 10 if name in RARE_POKEMON else 5
        if shiny:
            coins *= 2
        user["coins"] += coins

        shop_cog = bot.get_cog("Shop")
        if shop_cog:
            shop_cog.add_late_catch(message.channel.id, {
                "name": name,
                "dex": dex,
                "shiny": shiny
            })

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

        embed = discord.Embed(
            description=desc,
            color=0xFFD700 if shiny else 0xFF69B4
        )
        if sprite:
            embed.set_thumbnail(url=sprite)

        await message.channel.send(embed=embed)

        current_spawn = None
        data["current_spawn"] = None
        save_data(data)

    await bot.process_commands(message)

@bot.command()
async def starter(ctx):
    user_id = str(ctx.author.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "pokemon": [],
            "levels": {},
            "has_starter": False,
            "catches_without_starter": 0,
            "coins": 0,
            "inventory": {}
        }

    if data["users"][user_id].get("has_starter", False):
        await ctx.send("You already picked a starter!")
        return

    embed = discord.Embed(
        title="Choose your starter!",
        description="Reply with **1**, **2**, or **3**",
        color=0xFF69B4
    )
    embed.add_field(name="1. Bulbasaur", value="🌱 Grass type", inline=False)
    embed.add_field(name="2. Charmander", value="🔥 Fire type", inline=False)
    embed.add_field(name="3. Squirtle", value="💧 Water type", inline=False)
    embed.set_footer(text="You can only pick once!")
    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content in ["1", "2", "3"]

    try:
        reply = await bot.wait_for("message", check=check, timeout=60)
    except:
        await ctx.send("Took too long! Try `!starter` again.")
        return

    choice = STARTERS[reply.content]
    name = choice["name"]
    dex = choice["dex"]

    data["users"][user_id]["pokemon"].append({
        "name": name,
        "dex": dex,
        "caught_at": datetime.utcnow().isoformat(),
        "level": 1,
        "shiny": False,
        "nickname": None
    })
    data["users"][user_id].setdefault("levels", {})[name] = 1
    data["users"][user_id]["has_starter"] = True
    save_data(data)

    sprite = get_sprite(dex)
    embed = discord.Embed(
        title=f"You chose {name}!",
        description=f"**{ctx.author.display_name}** got a level 1 **{name}** as their starter!",
        color=0xFF69B4
    )
    embed.set_image(url=sprite)
    await ctx.send(embed=embed)

@bot.command()
async def spawn(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Only admins can force a spawn.")
        return

    global current_spawn
    if current_spawn:
        await ctx.send("There's already a Pokémon spawned!")
        return

    channel = ctx.channel
    dex, name = get_weighted_pokemon()
    shiny = random.random() < SHINY_CHANCE
    sprite = get_sprite(dex, shiny)

    current_spawn = {
        "name": name,
        "dex": dex,
        "sprite": sprite,
        "shiny": shiny,
        "spawned_at": datetime.utcnow().isoformat(),
        "channel_id": channel.id
    }
    data["current_spawn"] = current_spawn
    save_data(data)

    title = f"✨ A wild shiny {name} appeared!" if shiny else f"A wild {name} appeared!"
    embed = discord.Embed(title=title, description="Type **catch** to catch it!", color=0xFFD700 if shiny else 0xFF69B4)
    embed.set_image(url=sprite)
    await channel.send(embed=embed)
    await ctx.send("Spawned!")

@bot.command()
async def balance(ctx):
    fresh = load_data()
    user = fresh["users"].get(str(ctx.author.id), {})
    await ctx.send(f"You have **{user.get('coins', 0)}** coins.")

@bot.command()
async def give(ctx, amount: int = None, item: str = None):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Admins only.")
        return
    if amount is None:
        await ctx.send("Usage: `!give 500` or `!give 5 stone`")
        return

    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "pokemon": [], "levels": {}, "has_starter": False,
            "catches_without_starter": 0, "coins": 0, "inventory": {}
        }
    user = data["users"][user_id]
    user.setdefault("coins", 0)
    user.setdefault("inventory", {})

    if item:
        item = item.lower()
        user["inventory"][item] = user["inventory"].get(item, 0) + amount
        save_data(data)
        await ctx.send(f"Gave yourself **{amount} {item}**(s).")
    else:
        user["coins"] += amount
        save_data(data)
        await ctx.send(f"Gave yourself **{amount}** coins. Balance: {user['coins']}.")

@bot.command()
async def daily(ctx):
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "pokemon": [], "levels": {}, "has_starter": False,
            "catches_without_starter": 0, "coins": 0, "inventory": {}
        }
    user = data["users"][user_id]
    user.setdefault("coins", 0)

    last = user.get("last_daily")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.utcnow() < last_dt + timedelta(hours=24):
            hours = int((last_dt + timedelta(hours=24) - datetime.utcnow()).total_seconds() // 3600)
            await ctx.send(f"Already claimed. Try again in ~{hours} hours.")
            return

    user["coins"] += 25
    user["last_daily"] = datetime.utcnow().isoformat()
    save_data(data)
    await ctx.send(f"+25 coins! You now have **{user['coins']}**.")

@bot.command()
async def evolve(ctx, *, name: str = None):
    if not name:
        await ctx.send("Usage: `!evolve <pokemon>`")
        return

    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
        await ctx.send("You don't have any Pokémon.")
        return
    user = data["users"][user_id]

    last = user.get("last_evolve")
    if last:
        last_dt = datetime.fromisoformat(last)
        if datetime.utcnow() < last_dt + timedelta(hours=24):
            hours = int((last_dt + timedelta(hours=24) - datetime.utcnow()).total_seconds() // 3600)
            await ctx.send(f"Already used evolve. Try again in ~{hours} hours.")
            return

    target = None
    for p in user["pokemon"]:
        if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
            target = p
            break

    if not target or target["name"] not in EVO_MAP:
        await ctx.send("That Pokémon can't be evolved with !evolve.")
        return

    old = target["name"]
    target["name"] = EVO_MAP[old]
    user["last_evolve"] = datetime.utcnow().isoformat()
    save_data(data)
    await ctx.send(f"**{old}** evolved into **{target['name']}**!")

bot.run(TOKEN)