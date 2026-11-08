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
        latest = self.load_data()
        # Deep merge users so inventory doesn't get lost
        for uid, udata in data.get("users", {}).items():
            if uid not in latest["users"]:
                latest["users"][uid] = udata
            else:
                latest["users"][uid].update(udata)
                if "inventory" in udata:
                    latest["users"][uid]["inventory"] = udata["inventory"]
                if "pokemon" in udata:
                    latest["users"][uid]["pokemon"] = udata["pokemon"]
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(latest, f, indent=2)

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
        self.save_data(data)
        await ctx.send(f"Bought **{item}**! You now have {user['inventory'][item]}.")

    @commands.command()
    async def stone(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!stone <pokemon>`")
            return

        data = self.load_data()
        user = self.get_user(data, str(ctx.author.id))

        if user["inventory"].get("stone", 0) < 1:
            await ctx.send("You don't have any Evolution Stones.")
            return

        target = None
        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                target = p
                break

        if not target or target["name"] not in STONE_EVOLUTIONS:
            await ctx.send("That Pokémon can't be evolved with a stone.")
            return

        old = target["name"]
        target["name"] = STONE_EVOLUTIONS[old]
        if old in user["levels"]:
            user["levels"][target["name"]] = user["levels"].pop(old)
        user["inventory"]["stone"] -= 1
        self.save_data(data)
        await ctx.send(f"Your **{old}** evolved into **{target['name']}**!")

    @commands.command()
    async def candy(self, ctx, *, name: str = None):
        if not name:
            await ctx.send("Usage: `!candy <pokemon>`")
            return

        data = self.load_data()
        user = self.get_user(data, str(ctx.author.id))

        if user["inventory"].get("candy", 0) < 1:
            await ctx.send("You don't have any Rare Candies.")
            return

        for p in user["pokemon"]:
            if p["name"].lower() == name.lower() or (p.get("nickname") and p["nickname"].lower() == name.lower()):
                user["levels"][p["name"]] = user["levels"].get(p["name"], 1) + 1
                user["inventory"]["candy"] -= 1
                self.save_data(data)
                await ctx.send(f"**{p['name']}** is now level **{user['levels'][p['name']]}**!")
                return
        await ctx.send(f"You don't have a {name}.")

    @commands.command()
    async def charm(self, ctx):
        data = self.load_data()
        user = self.get_user(data, str(ctx.author.id))
        if user["inventory"].get("charm", 0) < 1:
            await ctx.send("You don't have a Shiny Charm.")
            return
        user["inventory"]["charm"] -= 1
        user["shiny_charm"] = True
        self.save_data(data)
        await ctx.send("Shiny Charm active! Next catch has higher shiny chance.")

    @commands.command()
    async def ball(self, ctx):
        await self._use_ball(ctx, "ball")

    @commands.command()
    async def greatball(self, ctx):
        await self._use_ball(ctx, "greatball")

    async def _use_ball(self, ctx, ball_type):
        data = self.load_data()
        user = self.get_user(data, str(ctx.author.id))
        if user["inventory"].get(ball_type, 0) < 1:
            await ctx.send(f"You don't have any {ball_type}s.")
            return

        recent = None
        now = datetime.utcnow()
        for cid, info in list(self.late_catches.items()):
            if now < info["expires"]:
                recent = info
                break
            else:
                del self.late_catches[cid]

        if not recent:
            await ctx.send("Nothing to late-catch.")
            return

        user["inventory"][ball_type] -= 1
        poke = recent["pokemon"]
        user["pokemon"].append({
            "name": poke["name"], "dex": poke["dex"],
            "shiny": poke.get("shiny", False), "nickname": None,
            "level": 1, "caught_at": now.isoformat()
        })
        if poke["name"] not in user["levels"]:
            user["levels"][poke["name"]] = 1
        self.save_data(data)
        await ctx.send(f"Late-caught a **{poke['name']}** with a {ball_type}!")

    def add_late_catch(self, channel_id, pokemon_data):
        self.late_catches[channel_id] = {
            "pokemon": pokemon_data,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }

async def setup(bot):
    await bot.add_cog(Shop(bot))