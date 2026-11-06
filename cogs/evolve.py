import discord
from discord.ext import commands
import json
import os

EVOLUTIONS = {
    "Bulbasaur": ("Ivysaur", 100),
    "Ivysaur": ("Venusaur", 100),
    "Charmander": ("Charmeleon", 100),
    "Charmeleon": ("Charizard", 100),
    "Squirtle": ("Wartortle", 100),
    "Wartortle": ("Blastoise", 100),
    "Caterpie": ("Metapod", 100),
    "Metapod": ("Butterfree", 100),
    "Weedle": ("Kakuna", 100),
    "Kakuna": ("Beedrill", 100),
    "Pidgey": ("Pidgeotto", 100),
    "Pidgeotto": ("Pidgeot", 100),
    "Rattata": ("Raticate", 100),
    "Spearow": ("Fearow", 100),
    "Ekans": ("Arbok", 100),
    "Pikachu": ("Raichu", 100),
    "Sandshrew": ("Sandslash", 100),
    "Nidoran♀": ("Nidorina", 100),
    "Nidorina": ("Nidoqueen", 100),
    "Nidoran♂": ("Nidorino", 100),
    "Nidorino": ("Nidoking", 100),
    "Clefairy": ("Clefable", 100),
    "Vulpix": ("Ninetales", 100),
    "Jigglypuff": ("Wigglytuff", 100),
    "Zubat": ("Golbat", 100),
    "Oddish": ("Gloom", 100),
    "Gloom": ("Vileplume", 100),
    "Paras": ("Parasect", 100),
    "Venonat": ("Venomoth", 100),
    "Diglett": ("Dugtrio", 100),
    "Meowth": ("Persian", 100),
    "Psyduck": ("Golduck", 100),
    "Mankey": ("Primeape", 100),
    "Growlithe": ("Arcanine", 100),
    "Poliwag": ("Poliwhirl", 100),
    "Poliwhirl": ("Poliwrath", 100),
    "Abra": ("Kadabra", 100),
    "Kadabra": ("Alakazam", 100),
    "Machop": ("Machoke", 100),
    "Machoke": ("Machamp", 100),
    "Bellsprout": ("Weepinbell", 100),
    "Weepinbell": ("Victreebel", 100),
    "Tentacool": ("Tentacruel", 100),
    "Geodude": ("Graveler", 100),
    "Graveler": ("Golem", 100),
    "Ponyta": ("Rapidash", 100),
    "Slowpoke": ("Slowbro", 100),
    "Magnemite": ("Magneton", 100),
    "Doduo": ("Dodrio", 100),
    "Seel": ("Dewgong", 100),
    "Grimer": ("Muk", 100),
    "Shellder": ("Cloyster", 100),
    "Gastly": ("Haunter", 100),
    "Haunter": ("Gengar", 100),
    "Drowzee": ("Hypno", 100),
    "Krabby": ("Kingler", 100),
    "Voltorb": ("Electrode", 100),
    "Exeggcute": ("Exeggutor", 100),
    "Cubone": ("Marowak", 100),
    "Koffing": ("Weezing", 100),
    "Rhyhorn": ("Rhydon", 100),
    "Horsea": ("Seadra", 100),
    "Goldeen": ("Seaking", 100),
    "Staryu": ("Starmie", 100),
    "Magikarp": ("Gyarados", 100),
    "Eevee": ("Vaporeon", 100),
    "Omanyte": ("Omastar", 100),
    "Kabuto": ("Kabutops", 100),
    "Dratini": ("Dragonair", 100),
    "Dragonair": ("Dragonite", 100),
}

class Evolve(commands.Cog):
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
    async def grind(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!grind <pokemon>`")
            return

        data = self.load_data()
        user_id = str(ctx.author.id)
        if user_id not in data["users"] or not data["users"][user_id].get("pokemon"):
            await ctx.send("You don't have any Pokémon yet.")
            return

        user = data["users"][user_id]
        found = False
        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                user["grinding"] = p["name"]
                user.setdefault("xp", {})
                user["xp"][p["name"]] = user["xp"].get(p["name"], 0)
                found = True
                break

        if not found:
            await ctx.send(f"You don't have a {name}.")
            return

        self.save_data(data)
        await ctx.send(f"Now grinding **{user['grinding']}**. Every message you send gives it XP!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        data = self.load_data()
        user_id = str(message.author.id)
        if user_id not in data["users"]:
            return

        user = data["users"][user_id]
        grinding = user.get("grinding")
        if not grinding:
            return

        user.setdefault("xp", {})
        user["xp"][grinding] = user["xp"].get(grinding, 0) + 1
        xp = user["xp"][grinding]

        # Level up every 20 XP
        level_xp = 20
        current_level = user.get("levels", {}).get(grinding, 1)
        new_level = (xp // level_xp) + 1
        if new_level > current_level:
            user.setdefault("levels", {})
            user["levels"][grinding] = new_level
            await message.channel.send(f"**{message.author.display_name}**'s **{grinding}** grew to level **{new_level}**!")

        # Evolution at 100 XP
        if grinding in EVOLUTIONS:
            evo_name, needed = EVOLUTIONS[grinding]
            if xp >= needed:
                for p in user["pokemon"]:
                    if p["name"] == grinding:
                        p["name"] = evo_name
                        if grinding in user.get("levels", {}):
                            user["levels"][evo_name] = user["levels"].pop(grinding)
                        user["xp"][evo_name] = 0
                        if "grinding" in user:
                            user["grinding"] = evo_name
                        break

                self.save_data(data)
                await message.channel.send(f"🎉 **{message.author.display_name}**'s **{grinding}** evolved into **{evo_name}**!")
                return

        if xp % 10 == 0:
            self.save_data(data)

async def setup(bot):
    await bot.add_cog(Evolve(bot))
