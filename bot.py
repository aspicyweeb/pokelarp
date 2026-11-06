import os
import discord
from discord.ext import commands, tasks
import random
import json
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
SPAWN_CHANNEL_ID = int(os.getenv("SPAWN_CHANNEL_ID", "0"))
DATA_PATH = os.getenv("DATA_PATH", "/data/pokelarp_data.json")
MIN_SPAWN_MINUTES = 30
MAX_SPAWN_MINUTES = 120

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

STARTERS = {
    "1": {"name": "Bulbasaur", "dex": 1},
    "2": {"name": "Charmander", "dex": 4},
    "3": {"name": "Squirtle", "dex": 7}
}

def get_sprite(dex_num):
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

def load_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {"users": {}, "current_spawn": None, "last_spawn": None}

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
    spawn_loop.start()

@tasks.loop(minutes=1)
async def spawn_loop():
    global current_spawn
    if current_spawn:
        return

    now = datetime.utcnow()
    last = data.get("last_spawn")
    if last:
        last_dt = datetime.fromisoformat(last)
        wait = timedelta(minutes=random.randint(MIN_SPAWN_MINUTES, MAX_SPAWN_MINUTES))
        if now < last_dt + wait:
            return

    channel = bot.get_channel(SPAWN_CHANNEL_ID)
    if not channel:
        return

    dex = random.randint(1, 151)
    name = POKEMON[dex - 1]
    sprite = get_sprite(dex)

    current_spawn = {
        "name": name,
        "dex": dex,
        "sprite": sprite,
        "spawned_at": now.isoformat()
    }
    data["current_spawn"] = current_spawn
    data["last_spawn"] = now.isoformat()
    save_data(data)

    embed = discord.Embed(
        title=f"A wild {name} appeared!",
        description="Type **catch** to catch it!",
        color=0xFF69B4
    )
    embed.set_image(url=sprite)
    embed.set_footer(text="Pokelarp • Gen 1")
    await channel.send(embed=embed)

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
                "catches_without_starter": 0
            }

        user = data["users"][user_id]

        if not user.get("has_starter", False) and user.get("catches_without_starter", 0) >= 2:
            await message.channel.send(
                f"**{message.author.display_name}**, you need to pick a starter first!\n"
                f"Use `!starter` to choose Bulbasaur, Charmander, or Squirtle before catching more."
            )
            return

        name = current_spawn["name"]
        dex = current_spawn["dex"]

        user["pokemon"].append({
            "name": name,
            "dex": dex,
            "caught_at": datetime.utcnow().isoformat(),
            "level": 1
        })

        if name not in user["levels"]:
            user["levels"][name] = 1
        else:
            user["levels"][name] += 1

        level = user["levels"][name]

        if not user.get("has_starter", False):
            user["catches_without_starter"] = user.get("catches_without_starter", 0) + 1

        reply = (
            f"🎉 **{message.author.display_name}** caught a **{name}**!\n"
            f"Your {name} is now level **{level}**!"
        )

        if not user.get("has_starter", False):
            remaining = 2 - user["catches_without_starter"]
            if remaining > 0:
                reply += f"\n\nYou still need to pick a starter with `!starter` ({remaining} free catch left)."
            else:
                reply += "\n\nThat's your last free catch! Use `!starter` before you can catch more."

        await message.channel.send(reply)

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
            "catches_without_starter": 0
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
        "level": 1
    })
    data["users"][user_id]["levels"][name] = 1
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

    channel = bot.get_channel(SPAWN_CHANNEL_ID)
    dex = random.randint(1, 151)
    name = POKEMON[dex - 1]
    sprite = get_sprite(dex)

    current_spawn = {"name": name, "dex": dex, "sprite": sprite}
    data["current_spawn"] = current_spawn
    data["last_spawn"] = datetime.utcnow().isoformat()
    save_data(data)

    embed = discord.Embed(title=f"A wild {name} appeared!", description="Type **catch** to catch it!", color=0xFF69B4)
    embed.set_image(url=sprite)
    await channel.send(embed=embed)
    await ctx.send("Spawned!")

bot.run(TOKEN)
