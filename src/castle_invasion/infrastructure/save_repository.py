"""Persistência JSON versionada, validada e substituída atomicamente."""

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from castle_invasion.core.content import Content
from castle_invasion.entities.models import BattleState, Enemy, GameState, Inventory, Loot, Player, RoomState
from castle_invasion.infrastructure.content_loader import (
    number,
    object_keys,
    reject_duplicate_keys,
    require,
    text,
    validate_loot,
)


class SaveError(ValueError):
    """Falha ao salvar/carregar sem substituir a partida em memória."""


def encode_state(state: GameState, content: Content) -> dict:
    return {
        "save_version": 1,
        "campaign_hash": content.fingerprint,
        "player": asdict(state.player),
        "rooms": {key: asdict(room) for key, room in state.rooms.items()},
        "enemies": {key: asdict(enemy) for key, enemy in state.enemies.items()},
        "battle": asdict(state.battle) if state.battle else None,
        "visited": sorted(state.visited),
        "won": state.won,
    }


def save_game(path: Path, state: GameState, content: Content) -> None:
    temporary = None
    try:
        payload = json.dumps(encode_state(state, content), ensure_ascii=False, indent=2, allow_nan=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except (OSError, ValueError) as exc:
        raise SaveError(f"Não foi possível salvar: {exc}") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)


def _position(value, content, nullable=False):
    if nullable and value is None:
        return None
    require(isinstance(value, list) and len(value) == 2 and all(type(v) is int for v in value), "Posição inválida.")
    r, c = value
    world = content["map"]
    require(0 <= r < len(world) and 0 <= c < len(world[r]) and world[r][c] is not None, "Posição fora do mapa.")
    return r, c


def decode_state(data, content: Content) -> GameState:
    object_keys(
        data, ("save_version", "campaign_hash", "player", "rooms", "enemies", "battle", "visited", "won"), (), "save"
    )
    require(type(data["save_version"]) is int and data["save_version"] == 1, "Versão do save não suportada.")
    require(
        data["campaign_hash"] == content.fingerprint,
        "O save pertence a outra versão da campanha. Use os dados originais ou inicie uma nova partida.",
    )
    p = data["player"]
    object_keys(
        p, ("name", "health", "max_health", "position", "inventory", "last_position", "xp", "level"), (), "player"
    )
    text(p["name"], "player.name")
    require(len(p["name"]) <= 40, "Nome do jogador longo demais.")
    number(p["max_health"], "player.max_health", 1)
    number(p["health"], "player.health", 0, p["max_health"])
    number(p["xp"], "player.xp", integer=True)
    number(p["level"], "player.level", 1, integer=True)
    require(p["level"] == 1 + p["xp"] // content["rules"]["xp_per_level"], "Nível inconsistente com XP.")
    expected_health = content["player"]["max_health"] + (p["level"] - 1) * content["rules"]["health_per_level"]
    require(p["max_health"] == expected_health, "Vida máxima inconsistente com o nível.")
    position = _position(p["position"], content)
    last = _position(p["last_position"], content, nullable=True)
    if last is not None:
        require(abs(last[0] - position[0]) + abs(last[1] - position[1]) == 1, "Última sala deve ser adjacente.")
    inv = p["inventory"]
    object_keys(inv, ("weapons", "active_slot", "heal", "items"), (), "inventory")
    require(isinstance(inv["weapons"], list) and len(inv["weapons"]) == 3, "O inventário deve ter três slots.")
    for weapon in inv["weapons"]:
        require(
            weapon is None or isinstance(weapon, str) and weapon in content["weapons"], "Arma desconhecida no save."
        )
    number(inv["active_slot"], "inventory.active_slot", 0, 2, integer=True)
    require(
        inv["heal"] is None or isinstance(inv["heal"], str) and inv["heal"] in content["heals"],
        "Cura desconhecida no save.",
    )
    require(isinstance(inv["items"], dict), "inventory.items: objeto esperado.")
    for key, amount in inv["items"].items():
        require(key in content["items"], "Item desconhecido no save.")
        number(amount, f"inventory.items.{key}", 1, integer=True)
    player = Player(
        p["name"],
        p["health"],
        p["max_health"],
        position,
        Inventory(list(inv["weapons"]), inv["active_slot"], inv["heal"], dict(inv["items"])),
        last,
        p["xp"],
        p["level"],
    )

    require(
        isinstance(data["rooms"], dict) and set(data["rooms"]) == set(content["rooms"]), "Salas incompatíveis no save."
    )
    rooms = {}
    for key, room in data["rooms"].items():
        object_keys(room, ("inspected", "ground"), (), f"rooms.{key}")
        require(type(room["inspected"]) is bool, "Flag inspected inválida.")
        validate_loot(room["ground"], content.data, f"rooms.{key}.ground")
        rooms[key] = RoomState(room["inspected"], [Loot(**entry) for entry in room["ground"]])
    require(
        isinstance(data["enemies"], dict) and set(data["enemies"]) == set(content["enemies"]),
        "Inimigos incompatíveis no save.",
    )
    enemies = {}
    for key, enemy in data["enemies"].items():
        object_keys(enemy, ("id", "health", "rewarded"), (), f"enemies.{key}")
        require(enemy["id"] == key, "ID de inimigo inconsistente.")
        number(enemy["health"], f"enemies.{key}.health", 0, content["enemies"][key]["health"])
        require(
            type(enemy["rewarded"]) is bool and enemy["rewarded"] == (enemy["health"] == 0),
            "Estado de recompensa inconsistente.",
        )
        enemies[key] = Enemy(key, enemy["health"], enemy["rewarded"])
    expected_xp = sum(content["enemies"][key]["xp"] for key, enemy in enemies.items() if enemy.rewarded)
    require(player.xp == expected_xp, "XP inconsistente com os inimigos derrotados.")
    battle = None
    if data["battle"] is not None:
        b = data["battle"]
        object_keys(b, ("enemy_id", "cooldown"), (), "battle")
        text(b["enemy_id"], "battle.enemy_id")
        require(b["enemy_id"] in enemies and enemies[b["enemy_id"]].alive, "Combate com inimigo inválido.")
        require(
            content["enemies"][b["enemy_id"]]["placement"] == content.room_at(position), "Inimigo fora da sala atual."
        )
        max_cooldown = content["heals"][inv["heal"]]["cooldown"] if inv["heal"] else 0
        number(b["cooldown"], "battle.cooldown", 0, max_cooldown, integer=True)
        battle = BattleState(b["enemy_id"], b["cooldown"])
    else:
        require(
            not any(
                e.alive and content["enemies"][key]["placement"] == content.room_at(position)
                for key, e in enemies.items()
            ),
            "Inimigo vivo sem combate na sala atual.",
        )
    visited = data["visited"]
    require(
        isinstance(visited, list) and all(isinstance(r, str) and r in rooms for r in visited),
        "Salas visitadas inválidas.",
    )
    require(
        content.room_at(position) in visited and (last is None or content.room_at(last) in visited),
        "Sala atual/anterior não foi visitada.",
    )
    require(type(data["won"]) is bool, "Flag won inválida.")
    if data["won"]:
        objective = content["objective"]
        require(
            player.alive
            and battle is None
            and content.room_at(position) == objective["room"]
            and inv["items"].get(objective["key"], 0) > 0,
            "Vitória inconsistente.",
        )
    return GameState(player, rooms, enemies, battle, set(visited), data["won"])


def load_game(path: Path, content: Content) -> GameState:
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
        return decode_state(data, content)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, OverflowError) as exc:
        raise SaveError(f"Não foi possível carregar o save: {exc}") from exc
