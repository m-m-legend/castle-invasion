"""Carrega JSON e valida referências antes de iniciar a partida."""

import hashlib
import json
import math
from importlib.resources import files
from pathlib import Path

from castle_invasion.core.content import Content


class ContentError(ValueError):
    """Dados de campanha inválidos, com localização legível para o autor."""


def require(condition, message):
    if not condition:
        raise ContentError(message)


def number(value, path, minimum=0, maximum=None, integer=False):
    valid = type(value) in ((int,) if integer else (int, float))
    require(valid and math.isfinite(value), f"{path}: número finito esperado.")
    require(value >= minimum and (maximum is None or value <= maximum), f"{path}: valor fora dos limites.")


def text(value, path):
    require(isinstance(value, str) and bool(value.strip()), f"{path}: texto não vazio esperado.")
    require(all(ord(c) >= 32 for c in value), f"{path}: caracteres de controle não permitidos.")


def object_keys(value, required, optional, path):
    require(isinstance(value, dict), f"{path}: objeto esperado.")
    require(set(required) <= value.keys(), f"{path}: faltam campos {sorted(set(required) - value.keys())}.")
    require(
        value.keys() <= set(required) | set(optional),
        f"{path}: campos desconhecidos {sorted(value.keys() - set(required) - set(optional))}.",
    )


def validate_loot(entries, data, path):
    require(isinstance(entries, list), f"{path}: lista esperada.")
    for i, entry in enumerate(entries):
        where = f"{path}[{i}]"
        object_keys(entry, ("kind", "id"), (), where)
        text(entry["kind"], where + ".kind")
        text(entry["id"], where + ".id")
        group = {"item": "items", "weapon": "weapons", "heal": "heals"}.get(entry["kind"])
        require(group is not None and entry["id"] in data[group], f"{where}: tipo ou ID inexistente.")


def validate_content(data):
    root_keys = (
        "schema_version",
        "title",
        "map",
        "rooms",
        "weapons",
        "items",
        "heals",
        "enemies",
        "sprites",
        "player",
        "rules",
        "objective",
    )
    object_keys(data, root_keys, (), "campanha")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema_version não suportada.")
    text(data["title"], "title")
    for group in ("rooms", "weapons", "items", "heals", "enemies"):
        require(isinstance(data[group], dict), f"{group}: objeto esperado.")
        for key in data[group]:
            text(key, group + ".id")
    world = data["map"]
    require(isinstance(world, list) and bool(world), "map: lista de linhas não vazia esperada.")
    rooms = []
    for row in world:
        require(isinstance(row, list) and bool(row), "map: cada linha precisa ser uma lista não vazia.")
        for cell in row:
            if cell is not None:
                text(cell, "map.sala")
                rooms.append(cell)
    require(bool(rooms) and len(rooms) == len(set(rooms)), "map: salas devem ser únicas.")
    require(set(rooms) == set(data["rooms"]), "map e rooms devem conter exatamente as mesmas salas.")

    for key, weapon in data["weapons"].items():
        path = f"weapons.{key}"
        object_keys(weapon, ("name", "damage", "type"), ("block", "boost"), path)
        text(weapon["name"], path + ".name")
        require(weapon["type"] in ("melee", "ranged", "magic", "defense"), path + ": tipo desconhecido.")
        number(weapon["damage"], path + ".damage", 0.01)
        if "block" in weapon:
            number(weapon["block"], path + ".block", 0, 1)
        if "boost" in weapon:
            number(weapon["boost"], path + ".boost", 0.01)
    for key, heal in data["heals"].items():
        path = f"heals.{key}"
        object_keys(heal, ("name", "heal_fraction", "enemy_damage_multiplier", "cooldown", "message"), (), path)
        text(heal["name"], path + ".name")
        text(heal["message"], path + ".message")
        number(heal["heal_fraction"], path + ".heal_fraction", 0.01, 1)
        number(heal["enemy_damage_multiplier"], path + ".enemy_damage_multiplier", 0, 1)
        number(heal["cooldown"], path + ".cooldown", 0, integer=True)
    for key, item in data["items"].items():
        path = f"items.{key}"
        object_keys(item, ("name", "description", "type"), ("usage", "health_restore"), path)
        text(item["name"], path + ".name")
        text(item["description"], path + ".description")
        require(item["type"] in ("key", "consumable"), path + ": tipo desconhecido.")
        if "usage" in item:
            text(item["usage"], path + ".usage")
        if item["type"] == "consumable":
            number(item.get("health_restore"), path + ".health_restore", 0.01)

    sprites = data["sprites"]
    object_keys(sprites, ("castle", "player", "enemies"), (), "sprites")
    require(isinstance(sprites["enemies"], dict), "sprites.enemies: objeto esperado.")
    for label, lines in [("castle", sprites["castle"]), ("player", sprites["player"]), *sprites["enemies"].items()]:
        require(
            isinstance(lines, list)
            and all(isinstance(line, str) and all(ord(c) >= 32 for c in line) for line in lines),
            f"sprites.{label}: lista de linhas sem controles esperada.",
        )
    for key, enemy in data["enemies"].items():
        path = f"enemies.{key}"
        object_keys(enemy, ("name", "health", "damage", "sprite_key", "placement", "loot", "xp"), (), path)
        text(enemy["name"], path + ".name")
        text(enemy["placement"], path + ".placement")
        text(enemy["sprite_key"], path + ".sprite_key")
        number(enemy["health"], path + ".health", 0.01)
        number(enemy["damage"], path + ".damage")
        number(enemy["xp"], path + ".xp", integer=True)
        require(enemy["placement"] in data["rooms"], path + ": sala inexistente.")
        require(enemy["sprite_key"] in sprites["enemies"], path + ": sprite inexistente.")
        validate_loot(enemy["loot"], data, path + ".loot")
    for key, room in data["rooms"].items():
        path = f"rooms.{key}"
        object_keys(room, ("description", "loot"), (), path)
        require(isinstance(room["description"], list) and bool(room["description"]), path + ": descrição esperada.")
        for line in room["description"]:
            text(line, path + ".description")
        validate_loot(room["loot"], data, path + ".loot")

    player = data["player"]
    object_keys(player, ("max_health", "start_room", "weapons", "items", "heal"), (), "player")
    number(player["max_health"], "player.max_health", 1)
    text(player["start_room"], "player.start_room")
    require(player["start_room"] in rooms, "player.start_room: sala inexistente.")
    require(
        isinstance(player["weapons"], list) and len(player["weapons"]) <= 3, "player.weapons: no máximo três armas."
    )
    for weapon in player["weapons"]:
        text(weapon, "player.weapons")
        require(weapon in data["weapons"], "player.weapons: arma inexistente.")
    require(isinstance(player["items"], list), "player.items: lista esperada.")
    for item in player["items"]:
        text(item, "player.items")
        require(item in data["items"], "player.items: item inexistente.")
    require(
        player["heal"] is None or isinstance(player["heal"], str) and player["heal"] in data["heals"],
        "player.heal: cura inexistente.",
    )
    rules = data["rules"]
    object_keys(
        rules,
        (
            "unarmed_damage",
            "base_block",
            "xp_per_level",
            "health_per_level",
            "damage_per_level",
            "flee_damage_multiplier",
        ),
        (),
        "rules",
    )
    number(rules["unarmed_damage"], "rules.unarmed_damage", 0.01)
    number(rules["base_block"], "rules.base_block", 0, 1)
    number(rules["xp_per_level"], "rules.xp_per_level", 1, integer=True)
    for key in ("health_per_level", "damage_per_level", "flee_damage_multiplier"):
        number(rules[key], f"rules.{key}")
    objective = data["objective"]
    object_keys(objective, ("room", "key", "message"), (), "objective")
    for key in objective:
        text(objective[key], f"objective.{key}")
    require(objective["room"] in rooms, "objective.room: sala inexistente.")
    require(
        objective["key"] in data["items"] and data["items"][objective["key"]]["type"] == "key",
        "objective.key: chave inexistente.",
    )
    obtainable = set(player["items"])
    for definition in [*data["rooms"].values(), *data["enemies"].values()]:
        obtainable.update(entry["id"] for entry in definition["loot"] if entry["kind"] == "item")
    require(objective["key"] in obtainable, "objective.key: a chave não pode ser obtida nesta campanha.")

    # Garante conectividade espacial, inclusive para mapas irregulares e células vazias.
    positions = {name: (r, c) for r, row in enumerate(world) for c, name in enumerate(row) if name}
    todo = [positions[player["start_room"]]]
    seen = set(todo)
    while todo:
        r, c = todo.pop()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < len(world) and 0 <= nc < len(world[nr]) and world[nr][nc] is not None and (nr, nc) not in seen:
                seen.add((nr, nc))
                todo.append((nr, nc))
    require(len(seen) == len(rooms), "map: existem salas inacessíveis a partir da entrada.")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContentError(f"JSON: chave duplicada {key!r}.")
        result[key] = value
    return result


def load_content(path: Path | None = None) -> Content:
    source = path if path is not None else files("castle_invasion.data").joinpath("campaign.json")
    try:
        data = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
        validate_content(data)
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        raise ContentError(f"Não foi possível carregar a campanha: {exc}") from exc
    return Content(data, hashlib.sha256(canonical.encode("utf-8")).hexdigest())
