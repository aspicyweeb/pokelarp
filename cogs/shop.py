import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

STONE_EVOLUTIONS = {
    "Caterpie": "Metapod", "Metapod": "Butterfree", "Weedle": "Kakuna", "Kakuna": "Beedrill",
    "Pidgey": "Pidgeotto", "Pidgeotto": "Pidgeot", "Rattata": "Raticate", "Spearow": "Fearow",
    "Ekans": "Arbok", "Pikachu": "Raichu", "Sandshrew": "Sandslash",
    "Nidoran♀": "Nidorina", "Nidorina": "Nidoqueen", "Nidoran♂": "Nidorino", "Nidorino": "Nidoking",
    "Clefairy": "Clefable", "Vulpix": "Ninetales", "Jigglypuff": "Wigglytuff", "Zubat": "Golbat",
    "Oddish": "Gloom", "Gloom": "Vileplume", "Paras": "Parasect", "Venonat": "Venomoth",
    "Diglett": "Dugtrio", "Meowth": "Persian", "Psyduck": "Golduck", "Mankey": "Primeape",
    "Growlithe": "Arcanine", "Poliwag": "Poliwhirl", "Poliwhirl": "Poliwrath",
    "Abra": "Kadabra", "Kadabra": "Alakazam", "Machop": "Machoke", "Machoke": "Machamp",
    "Bellsprout": "Weepinbell", "Weepinbell": "Victreebel", "Tentacool": "Tentacruel",
    "Geodude": "Graveler", "Graveler": "Golem", "Ponyta": "Rapidash", "Slowpoke": "Slowbro",
    "Magnemite": "Magneton", "Doduo": "Dodrio", "Seel": "Dewgong", "Grimer": "Muk",
    "Shellder": "Cloyster", "Gastly": "Haunter", "Haunter": "Gengar", "Drowzee": "Hypno",
    "Krabby": "Kingler", "Voltorb": "Electrode", "Exeggcute": "Exeggutor", "Cubone": "Marowak",
    "Koffing": "Weezing", "Rhyhorn": "Rhydon", "Horsea": "Seadra", "Goldeen": "Seaking",
    "Staryu": "Starmie", "Magikarp": "Gyarados", "Eevee": "Vaporeon",
    "Omanyte": "Omastar", "Kabuto": "Kabutops", "Dratini": "Dragonair", "Dragonair": "Dragonite",
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.getenv("DATA_PATH", "/data/pokelarp_data.json")
        self.late_catches = {}

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                data = json.load(f)
                data.setdefault("users", {})
                return data
        return {"users": {}}

    def save_data(self, data):
        # Nuclear option — main bot handles all saves
        pass

    def get_user(self, data, user_id):
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "pokemon": [], "levels": {}, "has_starter": False,
                "catches_without_starter": 0, "coins": 0, "inventory": {}
            }
        user = data["users"][user_id]
        user.setdefault("coins", 0)
        user.setdefault("inventory", {})
        user.setdefault("pokemon", [])
        user.setdefault("levels", {})
        return user

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="PokéLarp Shop", description="Spend your coins!", color=0xFF69B4)
        embed.add_field(name="Poké Ball — 50", value="`!buy ball`", inline=True)
        embed.add_field(name="Great Ball — 100", value="`!buy greatball`", inline=True)
        embed.add_field(name="Rare Candy — 75", value="`!buy candy`", inline=True)
        embed.add_field(name="Evolution Stone — 150", value="`!buy stone`", inline=True)
        embed.add_field(name="Shiny Charm — 200", value="`!buy charm`", inline=True)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item: str = None):
        prices = {"ball": 50, "greatball": 100, "candy": 75, "stone": 150, "charm": 200}
        if not item or item.lower() not in prices:
            await ctx.send("Usage: `!buy ball|greatball|candy|stone|charm`")
            return

        item = item.lower()
        data = self.load_data()
        user = self.get_user(data, str(ctx.author.id))
        cost = prices[item]

        if user["coins"] < cost:
            await ctx.send(f"Need {cost} coins. You have {user['coins']}.")
            return

        user["coins"] -= cost
        user["inventory"][item] = user["inventory"].get(item, 0) + 1
        # Note: changes won't stick until main bot saves
        await ctx.send(f"Bought **{item}**! (Note: shop saves are temporarily disabled)")

    @commands.command()
    async def stone(self, ctx, *, name: str = None):
        await ctx.send("Shop item use is temporarily disabled while we fix saving.")

    @commands.command()
    async def candy(self, ctx, *, name: str = None):
        await ctx.send("Shop item use is temporarily disabled while we fix saving.")

    @commands.command()
    async def charm(self, ctx):
        await ctx.send("Shop item use is temporarily disabled while we fix saving.")

    @commands.command()
    async def ball(self, ctx):
        await ctx.send("Shop item use is temporarily disabled while we fix saving.")

    @commands.command()
    async def greatball(self, ctx):
        await ctx.send("Shop item use is temporarily disabled while we fix saving.")

    def add_late_catch(self, channel_id, pokemon_data):
        self.late_catches[channel_id] = {
            "pokemon": pokemon_data,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }

async def setup(bot):
    await bot.add_cog(Shop(bot))