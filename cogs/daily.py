import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

# Commons that can evolve (no starters, no Eeveelutions, no legendaries)
COMMON_EVOLUTIONS = {
    "Caterpie": "Metapod",
    "Metapod": "Butterfree",
    "Weedle": "Kakuna",
    "Kakuna": "Beedrill",
    "Pidgey": "Pidgeotto",
    "Pidgeotto": "Pidgeot",
    "Rattata": "Raticate",
    "Spearow": "Fearow",
    "Ekans": "Arbok",
    "Sandshrew": "Sandslash",
    "Nidoran♀": "Nidorina",
    "Nidorina": "Nidoqueen",
    "Nidoran♂": "Nidorino",
    "Nidorino": "Nidoking",
    "Clefairy": "Clefable",
    "Vulpix": "Ninetales",
    "Jigglypuff": "Wigglytuff",
    "Zubat": "Golbat",
    "Oddish": "Gloom",
    "Gloom": "Vileplume",
    "Paras": "Parasect",
    "Venonat": "Venomoth",
    "Diglett": "Dugtrio",
    "Meowth": "Persian",
    "Psyduck": "Golduck",
    "Mankey": "Primeape",
    "Growlithe": "Arcanine",
    "Poliwag": "Poliwhirl",
    "Poliwhirl": "Poliwrath",
    "Abra": "Kadabra",
    "Kadabra": "Alakazam",
    "Machop": "Machoke",
    "Machoke": "Machamp",
    "Bellsprout": "Weepinbell",
    "Weepinbell": "Victreebel",
    "Tentacool": "Tentacruel",
    "Geodude": "Graveler",
    "Graveler": "Golem",
    "Ponyta": "Rapidash",
    "Slowpoke": "Slowbro",
    "Magnemite": "Magneton",
    "Doduo": "Dodrio",
    "Seel": "Dewgong",
    "Grimer": "Muk",
    "Shellder": "Cloyster",
    "Gastly": "Haunter",
    "Haunter": "Gengar",
    "Drowzee": "Hypno",
    "Krabby": "Kingler",
    "Voltorb": "Electrode",
    "Exeggcute": "Exeggutor",
    "Cubone": "Marowak",
    "Koffing": "Weezing",
    "Rhyhorn": "Rhydon",
    "Horsea": "Seadra",
    "Goldeen": "Seaking",
    "Staryu": "Starmie",
    "Magikarp": "Gyarados",
    "Omanyte": "Omastar",
    "Kabuto": "Kabutops",
    "Dratini": "Dragonair",
    "Dragonair": "Dragonite",
}

class Daily(commands.Cog):
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

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)

    @commands.command()
    async def daily(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!daily <pokemon>` — evolve one common Pokémon (once per day)")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon yet.")
            return

        user = data["users"][user_id]
        last = user.get("last_daily")
        if last:
            last_dt = datetime.fromisoformat(last)
            if datetime.utcnow() < last_dt + timedelta(hours=24):
                remaining = (last_dt + timedelta(hours=24) - datetime.utcnow())
                hours = int(remaining.total_seconds() // 3600)
                await ctx.send(f"You already used your daily. Try again in ~{hours} hours.")
                return

        # Find the Pokémon
        target = None
        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                target = p
                break

        if not target:
            await ctx.send(f"You don't have a {name}.")
            return

        if target["name"] not in COMMON_EVOLUTIONS:
            await ctx.send(f"**{target['name']}** can't be evolved with daily (only commons).")
            return

        evo = COMMON_EVOLUTIONS[target["name"]]
        old_name = target["name"]
        target["name"] = evo

        # Update levels key if needed
        if old_name in user.get("levels", {}):
            user["levels"][evo] = user["levels"].pop(old_name)

        user["last_daily"] = datetime.utcnow().isoformat()
        self.save_data(data)

        await ctx.send(f"🎉 Your **{old_name}** evolved into **{evo}**! (Daily used)")

async def setup(bot):
    await bot.add_cog(Daily(bot))