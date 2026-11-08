import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

# Evolutions that stones can do (includes more than just commons)
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
        latest = self.load_data()
        latest["users"].update(data.get("users", {}))
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(latest, f, indent=2)

    def ensure_user(self, data, user_id):
        if user_id not in data["users"]:
            data["users"][user_id] = {
                "pokemon": [], "levels": {}, "has_starter": False,
                "catches_without_starter": 0, "coins": 0, "inventory": {}
            }
        user = data["users"][user_id]
        user.setdefault("coins", 0)
        user.setdefault("inventory", {})
        return user

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="PokéLarp Shop", description="Spend your coins!", color=0xFF69B4)
        embed.add_field(name="Poké Ball — 50 coins", value="Late catch (5 min)\n`!buy ball`", inline=False)
        embed.add_field(name="Great Ball — 100 coins", value="Late catch (10 min)\n`!buy greatball`", inline=False)
        embed.add_field(name="Rare Candy — 75 coins", value="Level up a Pokémon by 1\n`!buy candy`", inline=False)
        embed.add_field(name="Evolution Stone — 150 coins", value="Evolve almost any Pokémon\n`!buy stone`", inline=False)
        embed.add_field(name="Shiny Charm — 200 coins", value="Next catch has higher shiny chance\n`!buy charm`", inline=False)
        embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item: str = None):
        if not item:
            await ctx.send("Usage: `!buy ball` | `greatball` | `candy` | `stone` | `charm`")
            return

        prices = {"ball": 50, "greatball": 100, "candy": 75, "stone": 150, "charm": 200}
        item = item.lower()
        if item not in prices:
            await ctx.send("Unknown item.")
            return

        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        cost = prices[item]
        if user["coins"] < cost:
            await ctx.send(f"You need {cost} coins. You have {user['coins']}.")
            return

        user["coins"] -= cost
        user["inventory"][item] = user["inventory"].get(item, 0) + 1
        self.save_data(data)
        await ctx.send(f"Bought a **{item}**! You now have {user['inventory'][item]}.")

    @commands.command()
    async def ball(self, ctx):
        await self.use_ball(ctx, "ball", 5)

    @commands.command()
    async def greatball(self, ctx):
        await self.use_ball(ctx, "greatball", 10)

    async def use_ball(self, ctx, ball_type, minutes):
        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["inventory"].get(ball_type, 0) < 1:
            await ctx.send(f"You don't have any {ball_type}s.")
            return

        recent = None
        for cid, info in list(self.late_catches.items()):
            if datetime.utcnow() < info["expires"]:
                recent = info
                break
            else:
                del self.late_catches[cid]

        if not recent:
            await ctx.send("Nothing to late-catch right now.")
            return

        user["inventory"][ball_type] -= 1
        poke = recent["pokemon"]
        user["pokemon"].append({
            "name": poke["name"], "dex": poke["dex"], "shiny": poke.get("shiny", False),
            "nickname": None, "level": 1, "caught_at": datetime.utcnow().isoformat()
        })
        if poke["name"] not in user.get("levels", {}):
            user.setdefault("levels", {})[poke["name"]] = 1
        self.save_data(data)
        await ctx.send(f"Used a {ball_type}! You late-caught a **{poke['name']}**!")

    @commands.command()
    async def candy(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!candy <pokemon>`")
            return
        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["inventory"].get("candy", 0) < 1:
            await ctx.send("You don't have any Rare Candies.")
            return

        found = False
        for p in user.get("pokemon", []):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                user.setdefault("levels", {})
                user["levels"][p["name"]] = user["levels"].get(p["name"], 1) + 1
                user["inventory"]["candy"] -= 1
                found = True
                self.save_data(data)
                await ctx.send(f"**{p['name']}** grew to level **{user['levels'][p['name']]}**!")
                break
        if not found:
            await ctx.send(f"You don't have a {name}.")

    @commands.command()
    async def stone(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!stone <pokemon>`")
            return
        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["inventory"].get("stone", 0) < 1:
            await ctx.send("You don't have any Evolution Stones.")
            return

        target = None
        for p in user.get("pokemon", []):
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                target = p
                break
        if not target or target["name"] not in STONE_EVOLUTIONS:
            await ctx.send("That Pokémon can't be evolved with a stone.")
            return

        old = target["name"]
        evo = STONE_EVOLUTIONS[old]
        target["name"] = evo
        if old in user.get("levels", {}):
            user["levels"][evo] = user["levels"].pop(old)
        user["inventory"]["stone"] -= 1
        self.save_data(data)
        await ctx.send(f"Your **{old}** evolved into **{evo}**!")

    @commands.command()
    async def charm(self, ctx):
        data = self.load_data()
        user = self.ensure_user(data, str(ctx.author.id))
        if user["inventory"].get("charm", 0) < 1:
            await ctx.send("You don't have a Shiny Charm.")
            return
        user["inventory"]["charm"] -= 1
        user["shiny_charm"] = True
        self.save_data(data)
        await ctx.send("Shiny Charm activated! Your next catch has a higher shiny chance.")

    def add_late_catch(self, channel_id, pokemon_data):
        self.late_catches[channel_id] = {
            "pokemon": pokemon_data,
            "expires": datetime.utcnow() + timedelta(minutes=10)  # covers both balls
        }

async def setup(bot):
    await bot.add_cog(Shop(bot))