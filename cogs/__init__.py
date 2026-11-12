"""Shared Pokémon data and the one save file.

This used to be split across bot.py and every cog. That is what wiped
catches, dailies, gifts, and trades. Keep this file. bot.py and the other
cogs import it.
"""
import random

POKEMON = ['Bulbasaur',
 'Ivysaur',
 'Venusaur',
 'Charmander',
 'Charmeleon',
 'Charizard',
 'Squirtle',
 'Wartortle',
 'Blastoise',
 'Caterpie',
 'Metapod',
 'Butterfree',
 'Weedle',
 'Kakuna',
 'Beedrill',
 'Pidgey',
 'Pidgeotto',
 'Pidgeot',
 'Rattata',
 'Raticate',
 'Spearow',
 'Fearow',
 'Ekans',
 'Arbok',
 'Pikachu',
 'Raichu',
 'Sandshrew',
 'Sandslash',
 'Nidoran♀',
 'Nidorina',
 'Nidoqueen',
 'Nidoran♂',
 'Nidorino',
 'Nidoking',
 'Clefairy',
 'Clefable',
 'Vulpix',
 'Ninetales',
 'Jigglypuff',
 'Wigglytuff',
 'Zubat',
 'Golbat',
 'Oddish',
 'Gloom',
 'Vileplume',
 'Paras',
 'Parasect',
 'Venonat',
 'Venomoth',
 'Diglett',
 'Dugtrio',
 'Meowth',
 'Persian',
 'Psyduck',
 'Golduck',
 'Mankey',
 'Primeape',
 'Growlithe',
 'Arcanine',
 'Poliwag',
 'Poliwhirl',
 'Poliwrath',
 'Abra',
 'Kadabra',
 'Alakazam',
 'Machop',
 'Machoke',
 'Machamp',
 'Bellsprout',
 'Weepinbell',
 'Victreebel',
 'Tentacool',
 'Tentacruel',
 'Geodude',
 'Graveler',
 'Golem',
 'Ponyta',
 'Rapidash',
 'Slowpoke',
 'Slowbro',
 'Magnemite',
 'Magneton',
 "Farfetch'd",
 'Doduo',
 'Dodrio',
 'Seel',
 'Dewgong',
 'Grimer',
 'Muk',
 'Shellder',
 'Cloyster',
 'Gastly',
 'Haunter',
 'Gengar',
 'Onix',
 'Drowzee',
 'Hypno',
 'Krabby',
 'Kingler',
 'Voltorb',
 'Electrode',
 'Exeggcute',
 'Exeggutor',
 'Cubone',
 'Marowak',
 'Hitmonlee',
 'Hitmonchan',
 'Lickitung',
 'Koffing',
 'Weezing',
 'Rhyhorn',
 'Rhydon',
 'Chansey',
 'Tangela',
 'Kangaskhan',
 'Horsea',
 'Seadra',
 'Goldeen',
 'Seaking',
 'Staryu',
 'Starmie',
 'Mr. Mime',
 'Scyther',
 'Jynx',
 'Electabuzz',
 'Magmar',
 'Pinsir',
 'Tauros',
 'Magikarp',
 'Gyarados',
 'Lapras',
 'Ditto',
 'Eevee',
 'Vaporeon',
 'Jolteon',
 'Flareon',
 'Porygon',
 'Omanyte',
 'Omastar',
 'Kabuto',
 'Kabutops',
 'Aerodactyl',
 'Snorlax',
 'Articuno',
 'Zapdos',
 'Moltres',
 'Dratini',
 'Dragonair',
 'Dragonite',
 'Mewtwo',
 'Mew']

RARITY = {'Abra': 35,
 'Articuno': 3,
 'Dratini': 15,
 'Eevee': 40,
 'Gastly': 35,
 'Growlithe': 40,
 'Lapras': 15,
 'Machop': 35,
 'Mew': 1,
 'Mewtwo': 2,
 'Moltres': 3,
 'Pikachu': 40,
 'Snorlax': 10,
 'Vulpix': 40,
 'Zapdos': 3,
 'default': 100}

RARE_POKEMON = {'Snorlax', 'Dratini', 'Zapdos', 'Mew', 'Mewtwo', 'Articuno', 'Lapras', 'Moltres'}

EVO_MAP = {'Abra': 'Kadabra',
 'Bellsprout': 'Weepinbell',
 'Caterpie': 'Metapod',
 'Cubone': 'Marowak',
 'Diglett': 'Dugtrio',
 'Doduo': 'Dodrio',
 'Dratini': 'Dragonair',
 'Drowzee': 'Hypno',
 'Ekans': 'Arbok',
 'Exeggcute': 'Exeggutor',
 'Gastly': 'Haunter',
 'Geodude': 'Graveler',
 'Goldeen': 'Seaking',
 'Grimer': 'Muk',
 'Growlithe': 'Arcanine',
 'Horsea': 'Seadra',
 'Koffing': 'Weezing',
 'Krabby': 'Kingler',
 'Machop': 'Machoke',
 'Magikarp': 'Gyarados',
 'Magnemite': 'Magneton',
 'Mankey': 'Primeape',
 'Meowth': 'Persian',
 'Oddish': 'Gloom',
 'Paras': 'Parasect',
 'Pidgey': 'Pidgeotto',
 'Poliwag': 'Poliwhirl',
 'Ponyta': 'Rapidash',
 'Psyduck': 'Golduck',
 'Rattata': 'Raticate',
 'Rhyhorn': 'Rhydon',
 'Sandshrew': 'Sandslash',
 'Seel': 'Dewgong',
 'Shellder': 'Cloyster',
 'Slowpoke': 'Slowbro',
 'Spearow': 'Fearow',
 'Staryu': 'Starmie',
 'Tentacool': 'Tentacruel',
 'Venonat': 'Venomoth',
 'Voltorb': 'Electrode',
 'Weedle': 'Kakuna',
 'Zubat': 'Golbat'}

STARTERS = {'1': {'dex': 1, 'name': 'Bulbasaur'},
 '2': {'dex': 4, 'name': 'Charmander'},
 '3': {'dex': 7, 'name': 'Squirtle'}}

# Paid stone evolutions, including second stages. Eevee's form is chosen in the command.
STONE_EVOLUTIONS = {'Abra': 'Kadabra',
 'Bellsprout': 'Weepinbell',
 'Caterpie': 'Metapod',
 'Clefairy': 'Clefable',
 'Cubone': 'Marowak',
 'Diglett': 'Dugtrio',
 'Doduo': 'Dodrio',
 'Dragonair': 'Dragonite',
 'Dratini': 'Dragonair',
 'Drowzee': 'Hypno',
 'Eevee': 'Vaporeon',
 'Ekans': 'Arbok',
 'Exeggcute': 'Exeggutor',
 'Gastly': 'Haunter',
 'Geodude': 'Graveler',
 'Gloom': 'Vileplume',
 'Goldeen': 'Seaking',
 'Graveler': 'Golem',
 'Grimer': 'Muk',
 'Growlithe': 'Arcanine',
 'Haunter': 'Gengar',
 'Horsea': 'Seadra',
 'Jigglypuff': 'Wigglytuff',
 'Kabuto': 'Kabutops',
 'Kadabra': 'Alakazam',
 'Kakuna': 'Beedrill',
 'Koffing': 'Weezing',
 'Krabby': 'Kingler',
 'Machoke': 'Machamp',
 'Machop': 'Machoke',
 'Magikarp': 'Gyarados',
 'Magnemite': 'Magneton',
 'Mankey': 'Primeape',
 'Meowth': 'Persian',
 'Metapod': 'Butterfree',
 'Nidoran♀': 'Nidorina',
 'Nidoran♂': 'Nidorino',
 'Nidorina': 'Nidoqueen',
 'Nidorino': 'Nidoking',
 'Oddish': 'Gloom',
 'Omanyte': 'Omastar',
 'Paras': 'Parasect',
 'Pidgeotto': 'Pidgeot',
 'Pidgey': 'Pidgeotto',
 'Pikachu': 'Raichu',
 'Poliwag': 'Poliwhirl',
 'Poliwhirl': 'Poliwrath',
 'Ponyta': 'Rapidash',
 'Psyduck': 'Golduck',
 'Rattata': 'Raticate',
 'Rhyhorn': 'Rhydon',
 'Sandshrew': 'Sandslash',
 'Seel': 'Dewgong',
 'Shellder': 'Cloyster',
 'Slowpoke': 'Slowbro',
 'Spearow': 'Fearow',
 'Staryu': 'Starmie',
 'Tentacool': 'Tentacruel',
 'Venonat': 'Venomoth',
 'Voltorb': 'Electrode',
 'Vulpix': 'Ninetales',
 'Weedle': 'Kakuna',
 'Weepinbell': 'Victreebel',
 'Zubat': 'Golbat'}

EEVEE_FORMS = {
    "vaporeon": "Vaporeon",
    "jolteon": "Jolteon",
    "flareon": "Flareon",
}

TYPES = {'Abra': ['Psychic'],
 'Aerodactyl': ['Rock', 'Flying'],
 'Alakazam': ['Psychic'],
 'Arbok': ['Poison'],
 'Arcanine': ['Fire'],
 'Articuno': ['Ice', 'Flying'],
 'Beedrill': ['Bug', 'Poison'],
 'Bellsprout': ['Grass', 'Poison'],
 'Blastoise': ['Water'],
 'Bulbasaur': ['Grass', 'Poison'],
 'Butterfree': ['Bug', 'Flying'],
 'Caterpie': ['Bug'],
 'Chansey': ['Normal'],
 'Charizard': ['Fire', 'Flying'],
 'Charmander': ['Fire'],
 'Charmeleon': ['Fire'],
 'Clefable': ['Fairy'],
 'Clefairy': ['Fairy'],
 'Cloyster': ['Water', 'Ice'],
 'Cubone': ['Ground'],
 'Dewgong': ['Water', 'Ice'],
 'Diglett': ['Ground'],
 'Ditto': ['Normal'],
 'Dodrio': ['Normal', 'Flying'],
 'Doduo': ['Normal', 'Flying'],
 'Dragonair': ['Dragon'],
 'Dragonite': ['Dragon', 'Flying'],
 'Dratini': ['Dragon'],
 'Drowzee': ['Psychic'],
 'Dugtrio': ['Ground'],
 'Eevee': ['Normal'],
 'Ekans': ['Poison'],
 'Electabuzz': ['Electric'],
 'Electrode': ['Electric'],
 'Exeggcute': ['Grass', 'Psychic'],
 'Exeggutor': ['Grass', 'Psychic'],
 "Farfetch'd": ['Normal', 'Flying'],
 'Fearow': ['Normal', 'Flying'],
 'Flareon': ['Fire'],
 'Gastly': ['Ghost', 'Poison'],
 'Gengar': ['Ghost', 'Poison'],
 'Geodude': ['Rock', 'Ground'],
 'Gloom': ['Grass', 'Poison'],
 'Golbat': ['Poison', 'Flying'],
 'Goldeen': ['Water'],
 'Golduck': ['Water'],
 'Golem': ['Rock', 'Ground'],
 'Graveler': ['Rock', 'Ground'],
 'Grimer': ['Poison'],
 'Growlithe': ['Fire'],
 'Gyarados': ['Water', 'Flying'],
 'Haunter': ['Ghost', 'Poison'],
 'Hitmonchan': ['Fighting'],
 'Hitmonlee': ['Fighting'],
 'Horsea': ['Water'],
 'Hypno': ['Psychic'],
 'Ivysaur': ['Grass', 'Poison'],
 'Jigglypuff': ['Normal', 'Fairy'],
 'Jolteon': ['Electric'],
 'Jynx': ['Ice', 'Psychic'],
 'Kabuto': ['Rock', 'Water'],
 'Kabutops': ['Rock', 'Water'],
 'Kadabra': ['Psychic'],
 'Kakuna': ['Bug', 'Poison'],
 'Kangaskhan': ['Normal'],
 'Kingler': ['Water'],
 'Koffing': ['Poison'],
 'Krabby': ['Water'],
 'Lapras': ['Water', 'Ice'],
 'Lickitung': ['Normal'],
 'Machamp': ['Fighting'],
 'Machoke': ['Fighting'],
 'Machop': ['Fighting'],
 'Magikarp': ['Water'],
 'Magmar': ['Fire'],
 'Magnemite': ['Electric', 'Steel'],
 'Magneton': ['Electric', 'Steel'],
 'Mankey': ['Fighting'],
 'Marowak': ['Ground'],
 'Meowth': ['Normal'],
 'Metapod': ['Bug'],
 'Mew': ['Psychic'],
 'Mewtwo': ['Psychic'],
 'Moltres': ['Fire', 'Flying'],
 'Mr. Mime': ['Psychic', 'Fairy'],
 'Muk': ['Poison'],
 'Nidoking': ['Poison', 'Ground'],
 'Nidoqueen': ['Poison', 'Ground'],
 'Nidoran♀': ['Poison'],
 'Nidoran♂': ['Poison'],
 'Nidorina': ['Poison'],
 'Nidorino': ['Poison'],
 'Ninetales': ['Fire'],
 'Oddish': ['Grass', 'Poison'],
 'Omanyte': ['Rock', 'Water'],
 'Omastar': ['Rock', 'Water'],
 'Onix': ['Rock', 'Ground'],
 'Paras': ['Bug', 'Grass'],
 'Parasect': ['Bug', 'Grass'],
 'Persian': ['Normal'],
 'Pidgeot': ['Normal', 'Flying'],
 'Pidgeotto': ['Normal', 'Flying'],
 'Pidgey': ['Normal', 'Flying'],
 'Pikachu': ['Electric'],
 'Pinsir': ['Bug'],
 'Poliwag': ['Water'],
 'Poliwhirl': ['Water'],
 'Poliwrath': ['Water', 'Fighting'],
 'Ponyta': ['Fire'],
 'Porygon': ['Normal'],
 'Primeape': ['Fighting'],
 'Psyduck': ['Water'],
 'Raichu': ['Electric'],
 'Rapidash': ['Fire'],
 'Raticate': ['Normal'],
 'Rattata': ['Normal'],
 'Rhydon': ['Ground', 'Rock'],
 'Rhyhorn': ['Ground', 'Rock'],
 'Sandshrew': ['Ground'],
 'Sandslash': ['Ground'],
 'Scyther': ['Bug', 'Flying'],
 'Seadra': ['Water'],
 'Seaking': ['Water'],
 'Seel': ['Water'],
 'Shellder': ['Water'],
 'Slowbro': ['Water', 'Psychic'],
 'Slowpoke': ['Water', 'Psychic'],
 'Snorlax': ['Normal'],
 'Spearow': ['Normal', 'Flying'],
 'Squirtle': ['Water'],
 'Starmie': ['Water', 'Psychic'],
 'Staryu': ['Water'],
 'Tangela': ['Grass'],
 'Tauros': ['Normal'],
 'Tentacool': ['Water', 'Poison'],
 'Tentacruel': ['Water', 'Poison'],
 'Vaporeon': ['Water'],
 'Venomoth': ['Bug', 'Poison'],
 'Venonat': ['Bug', 'Poison'],
 'Venusaur': ['Grass', 'Poison'],
 'Victreebel': ['Grass', 'Poison'],
 'Vileplume': ['Grass', 'Poison'],
 'Voltorb': ['Electric'],
 'Vulpix': ['Fire'],
 'Wartortle': ['Water'],
 'Weedle': ['Bug', 'Poison'],
 'Weepinbell': ['Grass', 'Poison'],
 'Weezing': ['Poison'],
 'Wigglytuff': ['Normal', 'Fairy'],
 'Zapdos': ['Electric', 'Flying'],
 'Zubat': ['Poison', 'Flying']}

NAME_TO_DEX = {name: i + 1 for i, name in enumerate(POKEMON)}

SHINY_CHANCE = 0.01
CHARM_SHINY_CHANCE = 0.05
SPAWN_LIFETIME_NOTE = "Spawns stay until caught. Each spawn channel has its own."

DEFAULT_SPAWN_CHANNELS = {
    1568206877286735872: {"min": 5, "max": 45},
    1540133768730509352: {"min": 30, "max": 120},
}

ALIASES = {
    "nidoran f": "nidoran♀",
    "nidoran female": "nidoran♀",
    "nidoranf": "nidoran♀",
    "nidoran-f": "nidoran♀",
    "nidoran m": "nidoran♂",
    "nidoran male": "nidoran♂",
    "nidoranm": "nidoran♂",
    "nidoran-m": "nidoran♂",
    "farfetchd": "farfetch'd",
    "farfetched": "farfetch'd",
    "mr mime": "mr. mime",
    "mr.mime": "mr. mime",
    "mrmime": "mr. mime",
}


def get_weighted_pokemon():
    weights = [RARITY.get(name, RARITY["default"]) for name in POKEMON]
    dex = random.choices(range(1, len(POKEMON) + 1), weights=weights, k=1)[0]
    return dex, POKEMON[dex - 1]


def get_sprite(dex_num, shiny=False):
    base = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
    if shiny:
        return f"{base}/shiny/{dex_num}.png"
    return f"{base}/{dex_num}.png"


def resolve_query(text):
    key = " ".join(text.strip().lower().split())
    return ALIASES.get(key, key)


def canonical_species(text):
    key = resolve_query(text)
    for name in POKEMON:
        if name.lower() == key:
            return name
    return None


def find_owned(user, query):
    """First pokemon whose species or nickname matches. None if they don't have it."""
    key = resolve_query(query)
    for mon in user.get("pokemon", []):
        nick = mon.get("nickname")
        if mon["name"].lower() == key or (nick and nick.lower() == key):
            return mon
    for mon in user.get("pokemon", []):
        if resolve_query(mon["name"]) == key:
            return mon
    return None


def mon_level(user, mon):
    own = mon.get("level")
    if isinstance(own, int) and own >= 1:
        return own
    return user.get("levels", {}).get(mon["name"], 1)


def apply_evolution(user, mon, new_name):
    old = mon["name"]
    level = mon_level(user, mon)
    mon["name"] = new_name
    mon["dex"] = NAME_TO_DEX[new_name]
    mon["level"] = level
    levels = user.setdefault("levels", {})
    levels[new_name] = max(levels.get(new_name, 1), level)
    return old


def catch_coins(name, shiny):
    coins = 10 if name in RARE_POKEMON else 5
    if shiny:
        coins *= 2
    return coins


def new_mon(name, dex, shiny, level=1, starter=False, caught_at=None):
    from datetime import datetime, timezone

    mon = {
        "name": name,
        "dex": dex,
        "caught_at": caught_at or datetime.now(timezone.utc).isoformat(),
        "level": level,
        "shiny": shiny,
        "nickname": None,
    }
    if starter:
        mon["starter"] = True
    return mon


def remember_species_level(user, name, level):
    levels = user.setdefault("levels", {})
    levels[name] = max(levels.get(name, 1), level)


def grant_catch(user, name, dex, shiny):
    """Add a caught pokemon and its coins. Mutates user in place."""
    mon = new_mon(name, dex, shiny)
    user.setdefault("pokemon", []).append(mon)
    remember_species_level(user, name, mon["level"])
    if not user.get("has_starter", False):
        user["catches_without_starter"] = user.get("catches_without_starter", 0) + 1
    coins = catch_coins(name, shiny)
    user["coins"] = user.get("coins", 0) + coins
    return mon, coins

import json
import os
from datetime import datetime, timedelta, timezone

DATA_PATH = os.getenv("DATA_PATH", "/data/pokelarp_data.json")

data = {
    "users": {},
    "spawns": {},
    "next_spawn": {},
    "spawn_channels": {},
    "trades": {},
    "late_catches": {},
}


def _empty():
    return {
        "users": {},
        "spawns": {},
        "next_spawn": {},
        "spawn_channels": {},
        "trades": {},
        "late_catches": {},
        "spawn_channels_seeded": False,
    }


def parse_dt(value):
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load():
    global data
    directory = os.path.dirname(DATA_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        data = _empty()
        _seed_channels()
        return data
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise RuntimeError(f"{DATA_PATH} is not a JSON object")
    loaded.setdefault("users", {})
    loaded.setdefault("spawns", {})
    loaded.setdefault("next_spawn", {})
    loaded.setdefault("spawn_channels", {})
    loaded.setdefault("trades", {})
    loaded.setdefault("late_catches", {})
    # Older builds kept a single global spawn, which blocked every channel.
    legacy = loaded.get("current_spawn")
    if legacy and isinstance(legacy, dict) and not loaded["spawns"]:
        channel_id = legacy.get("channel_id")
        if channel_id is not None:
            loaded["spawns"][str(channel_id)] = legacy
    loaded["current_spawn"] = None
    data = loaded
    seeded = _seed_channels(save_now=False)
    migrated = _migrate_last_spawns()
    if seeded or migrated or legacy:
        save()
    return data


def save():
    directory = os.path.dirname(DATA_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, DATA_PATH)


def _seed_channels(save_now=True):
    if data.get("spawn_channels_seeded"):
        return False
    for channel_id, rates in DEFAULT_SPAWN_CHANNELS.items():
        data["spawn_channels"].setdefault(
            str(channel_id), {"min": rates["min"], "max": rates["max"]}
        )
    data["spawn_channels_seeded"] = True
    if save_now:
        save()
    return True


def _migrate_last_spawns():
    """Old builds stored last_spawn_<channel> and rerolled the wait every minute.
    Keep a single future timestamp so a restart doesn't spawn everything at once.
    """
    now = datetime.now(timezone.utc)
    migrated = False
    for key, value in list(data.items()):
        if not isinstance(key, str) or not key.startswith("last_spawn_"):
            continue
        channel_id = key[len("last_spawn_") :]
        data.setdefault("next_spawn", {})
        if channel_id in data["next_spawn"]:
            continue
        try:
            last = parse_dt(value)
        except (TypeError, ValueError):
            continue
        rates = data.get("spawn_channels", {}).get(channel_id, {"min": 5})
        earliest = last + timedelta(minutes=int(rates.get("min", 5)))
        data["next_spawn"][channel_id] = (earliest if earliest > now else now).isoformat()
        migrated = True
    return migrated


def spawn_channel_map():
    """channel id -> {min, max} minutes. Includes admin-added channels."""
    result = {}
    for key, rates in data.get("spawn_channels", {}).items():
        try:
            channel_id = int(key)
        except (TypeError, ValueError):
            continue
        min_m = int(rates.get("min", 5))
        max_m = int(rates.get("max", min_m))
        result[channel_id] = {"min": min_m, "max": max(max_m, min_m)}
    return result


def set_spawn_rate(channel_id, min_minutes, max_minutes):
    data.setdefault("spawn_channels", {})[str(channel_id)] = {
        "min": min_minutes,
        "max": max_minutes,
    }
    save()


def remove_spawn_channel(channel_id):
    data.get("spawn_channels", {}).pop(str(channel_id), None)
    data.get("spawns", {}).pop(str(channel_id), None)
    data.get("next_spawn", {}).pop(str(channel_id), None)
    save()


def ensure_user(user_id):
    user_id = str(user_id)
    users = data.setdefault("users", {})
    if user_id not in users:
        users[user_id] = {
            "pokemon": [],
            "levels": {},
            "has_starter": False,
            "catches_without_starter": 0,
            "coins": 0,
            "inventory": {},
        }
    user = users[user_id]
    user.setdefault("pokemon", [])
    user.setdefault("levels", {})
    user.setdefault("has_starter", False)
    user.setdefault("catches_without_starter", 0)
    user.setdefault("coins", 0)
    user.setdefault("inventory", {})
    return user


def blank_user():
    return {
        "pokemon": [],
        "levels": {},
        "has_starter": False,
        "catches_without_starter": 0,
        "coins": 0,
        "inventory": {},
    }


def pop_pokemon(user, pred):
    for index, mon in enumerate(user.get("pokemon", [])):
        if pred(mon):
            return user["pokemon"].pop(index)
    return None


def cooldown_remaining(iso_value, hours):
    if not iso_value:
        return None
    ready_at = parse_dt(iso_value) + timedelta(hours=hours)
    now = datetime.now(timezone.utc)
    if now >= ready_at:
        return None
    return ready_at - now


def format_wait(delta):
    total = int(delta.total_seconds())
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{max(minutes, 1)}m"


def set_late_catch(channel_id, pokemon, when=None):
    when = when or datetime.now(timezone.utc)
    data.setdefault("late_catches", {})[str(channel_id)] = {
        "pokemon": {
            "name": pokemon["name"],
            "dex": pokemon["dex"],
            "shiny": bool(pokemon.get("shiny", False)),
        },
        "at": when.isoformat(),
    }


def get_late_catch(channel_id):
    entry = data.get("late_catches", {}).get(str(channel_id))
    if not entry:
        return None
    try:
        at = parse_dt(entry["at"])
    except (KeyError, ValueError):
        return None
    return entry["pokemon"], at


def mon_offered(mon):
    caught_at = mon.get("caught_at")
    for trade in data.get("trades", {}).values():
        for key in ("offer_a", "offer_b"):
            offer = trade.get(key)
            if not offer:
                continue
            if offer.get("caught_at") == caught_at and offer.get("name") == mon.get("name"):
                return True
    return False


def schedule_next_spawn(channel_id, when):
    data.setdefault("next_spawn", {})[str(channel_id)] = when.isoformat()


def next_spawn_at(channel_id):
    raw = data.get("next_spawn", {}).get(str(channel_id))
    if not raw:
        return None
    return parse_dt(raw)
