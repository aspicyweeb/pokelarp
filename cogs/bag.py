import discord
from discord.ext import commands
import json
import os

# Gen 1 types
TYPES = {
    "Bulbasaur": ["Grass", "Poison"], "Ivysaur": ["Grass", "Poison"], "Venusaur": ["Grass", "Poison"],
    "Charmander": ["Fire"], "Charmeleon": ["Fire"], "Charizard": ["Fire", "Flying"],
    "Squirtle": ["Water"], "Wartortle": ["Water"], "Blastoise": ["Water"],
    "Caterpie": ["Bug"], "Metapod": ["Bug"], "Butterfree": ["Bug", "Flying"],
    "Weedle": ["Bug", "Poison"], "Kakuna": ["Bug", "Poison"], "Beedrill": ["Bug", "Poison"],
    "Pidgey": ["Normal", "Flying"], "Pidgeotto": ["Normal", "Flying"], "Pidgeot": ["Normal", "Flying"],
    "Rattata": ["Normal"], "Raticate": ["Normal"], "Spearow": ["Normal", "Flying"], "Fearow": ["Normal", "Flying"],
    "Ekans": ["Poison"], "Arbok": ["Poison"], "Pikachu": ["Electric"], "Raichu": ["Electric"],
    "Sandshrew": ["Ground"], "Sandslash": ["Ground"], "Nidoran♀": ["Poison"], "Nidorina": ["Poison"], "Nidoqueen": ["Poison", "Ground"],
    "Nidoran♂": ["Poison"], "Nidorino": ["Poison"], "Nidoking": ["Poison", "Ground"],
    "Clefairy": ["Fairy"], "Clefable": ["Fairy"], "Vulpix": ["Fire"], "Ninetales": ["Fire"],
    "Jigglypuff": ["Normal", "Fairy"], "Wigglytuff": ["Normal", "Fairy"], "Zubat": ["Poison", "Flying"], "Golbat": ["Poison", "Flying"],
    "Oddish": ["Grass", "Poison"], "Gloom": ["Grass", "Poison"], "Vileplume": ["Grass", "Poison"],
    "Paras": ["Bug", "Grass"], "Parasect": ["Bug", "Grass"], "Venonat": ["Bug", "Poison"], "Venomoth": ["Bug", "Poison"],
    "Diglett": ["Ground"], "Dugtrio": ["Ground"], "Meowth": ["Normal"], "Persian": ["Normal"],
    "Psyduck": ["Water"], "Golduck": ["Water"], "Mankey": ["Fighting"], "Primeape": ["Fighting"],
    "Growlithe": ["Fire"], "Arcanine": ["Fire"], "Poliwag": ["Water"], "Poliwhirl": ["Water"], "Poliwrath": ["Water", "Fighting"],
    "Abra": ["Psychic"], "Kadabra": ["Psychic"], "Alakazam": ["Psychic"],
    "Machop": ["Fighting"], "Machoke": ["Fighting"], "Machamp": ["Fighting"],
    "Bellsprout": ["Grass", "Poison"], "Weepinbell": ["Grass", "Poison"], "Victreebel": ["Grass", "Poison"],
    "Tentacool": ["Water", "Poison"], "Tentacruel": ["Water", "Poison"],
    "Geodude": ["Rock", "Ground"], "Graveler": ["Rock", "Ground"], "Golem": ["Rock", "Ground"],
    "Ponyta": ["Fire"], "Rapidash": ["Fire"], "Slowpoke": ["Water", "Psychic"], "Slowbro": ["Water", "Psychic"],
    "Magnemite": ["Electric", "Steel"], "Magneton": ["Electric", "Steel"],
    "Farfetch'd": ["Normal", "Flying"], "Doduo": ["Normal", "Flying"], "Dodrio": ["Normal", "Flying"],
    "Seel": ["Water"], "Dewgong": ["Water", "Ice"], "Grimer": ["Poison"], "Muk": ["Poison"],
    "Shellder": ["Water"], "Cloyster": ["Water", "Ice"], "Gastly": ["Ghost", "Poison"], "Haunter": ["Ghost", "Poison"], "Gengar": ["Ghost", "Poison"],
    "Onix": ["Rock", "Ground"], "Drowzee": ["Psychic"], "Hypno": ["Psychic"],
    "Krabby": ["Water"], "Kingler": ["Water"], "Voltorb": ["Electric"], "Electrode": ["Electric"],
    "Exeggcute": ["Grass", "Psychic"], "Exeggutor": ["Grass", "Psychic"], "Cubone": ["Ground"], "Marowak": ["Ground"],
    "Hitmonlee": ["Fighting"], "Hitmonchan": ["Fighting"], "Lickitung": ["Normal"],
    "Koffing": ["Poison"], "Weezing": ["Poison"], "Rhyhorn": ["Ground", "Rock"], "Rhydon": ["Ground", "Rock"],
    "Chansey": ["Normal"], "Tangela": ["Grass"], "Kangaskhan": ["Normal"],
    "Horsea": ["Water"], "Seadra": ["Water"], "Goldeen": ["Water"], "Seaking": ["Water"],
    "Staryu": ["Water"], "Starmie": ["Water", "Psychic"], "Mr. Mime": ["Psychic", "Fairy"],
    "Scyther": ["Bug", "Flying"], "Jynx": ["Ice", "Psychic"], "Electabuzz": ["Electric"], "Magmar": ["Fire"],
    "Pinsir": ["Bug"], "Tauros": ["Normal"], "Magikarp": ["Water"], "Gyarados": ["Water", "Flying"],
    "Lapras": ["Water", "Ice"], "Ditto": ["Normal"], "Eevee": ["Normal"],
    "Vaporeon": ["Water"], "Jolteon": ["Electric"], "Flareon": ["Fire"], "Porygon": ["Normal"],
    "Omanyte": ["Rock", "Water"], "Omastar": ["Rock", "Water"], "Kabuto": ["Rock", "Water"], "Kabutops": ["Rock", "Water"],
    "Aerodactyl": ["Rock", "Flying"], "Snorlax": ["Normal"],
    "Articuno": ["Ice", "Flying"], "Zapdos": ["Electric", "Flying"], "Moltres": ["Fire", "Flying"],
    "Dratini": ["Dragon"], "Dragonair": ["Dragon"], "Dragonite": ["Dragon", "Flying"],
    "Mewtwo": ["Psychic"], "Mew": ["Psychic"]
}

class Bag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                data = json.load(f)
                data.setdefault("users", {})
                return data
        return {"users": {}}

    def get_sprite(self, dex_num, shiny=False):
        if shiny:
            return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{dex_num}.png"
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_num}.png"

    @commands.command()
    async def bag(self, ctx, filter: str = None):
        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You haven't caught any Pokémon yet!")
            return

        user = data["users"][user_id]
        pokemon = user.get("pokemon", [])
        coins = user.get("coins", 0)
        balls = user.get("inventory", {}).get("ball", 0)

        if not filter or filter.lower() in ["all", "pokemon", "pkmn"]:
            lines = []
            seen = {}
            for p in pokemon:
                key = p["name"]
                if key not in seen:
                    level = user.get("levels", {}).get(key, 1)
                    shiny = "✨ " if p.get("shiny") else ""
                    nick = f" ({p['nickname']})" if p.get("nickname") else ""
                    lines.append(f"{shiny}**{key}**{nick} — Lv.{level}")
                    seen[key] = True
            title = f"{ctx.author.display_name}'s Pokémon"
            desc = "\n".join(lines) if lines else "None"
            desc += f"\n\n**Coins:** {coins}\n**Poké Balls:** {balls}"

        elif filter.lower() in ["shiny", "shinies", "sparkle"]:
            lines = []
            for p in pokemon:
                if p.get("shiny"):
                    level = user.get("levels", {}).get(p["name"], 1)
                    nick = f" ({p['nickname']})" if p.get("nickname") else ""
                    lines.append(f"✨ **{p['name']}**{nick} — Lv.{level}")
            title = f"{ctx.author.display_name}'s Shinies"
            desc = "\n".join(lines) if lines else "No shinies yet!"

        elif filter.lower() in ["items", "shop", "inv", "inventory"]:
            title = f"{ctx.author.display_name}'s Items"
            desc = f"**Coins:** {coins}\n**Poké Balls:** {balls}"

        elif filter.lower() in TYPES or any(filter.lower() == t.lower() for types in TYPES.values() for t in types):
            # Type filter
            target_type = filter.capitalize()
            lines = []
            seen = {}
            for p in pokemon:
                p_types = TYPES.get(p["name"], [])
                if target_type in p_types and p["name"] not in seen:
                    level = user.get("levels", {}).get(p["name"], 1)
                    shiny = "✨ " if p.get("shiny") else ""
                    nick = f" ({p['nickname']})" if p.get("nickname") else ""
                    lines.append(f"{shiny}**{p['name']}**{nick} — Lv.{level}")
                    seen[p["name"]] = True
            title = f"{ctx.author.display_name}'s {target_type} Types"
            desc = "\n".join(lines) if lines else f"No {target_type} types yet!"

        else:
            await ctx.send("Usage: `!bag` | `!bag shinies` | `!bag items` | `!bag Fire` (or any type)")
            return

        embed = discord.Embed(title=title, description=desc, color=0xFF69B4)
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!info <pokemon>`")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"]:
            await ctx.send("You don't have any Pokémon yet.")
            return

        user = data["users"][user_id]
        found = None
        for p in user.get("pokemon", []):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                found = p
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        level = user.get("levels", {}).get(found["name"], 1)
        shiny = found.get("shiny", False)
        nick = found.get("nickname")
        display = nick if nick else found["name"]
        sprite = self.get_sprite(found["dex"], shiny)
        types = ", ".join(TYPES.get(found["name"], ["???"]))

        embed = discord.Embed(
            title=f"{'✨ ' if shiny else ''}{display}",
            description=f"**{found['name']}** — Level {level}\nType: {types}",
            color=0xFFD700 if shiny else 0xFF69B4
        )
        embed.set_image(url=sprite)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bag(bot))