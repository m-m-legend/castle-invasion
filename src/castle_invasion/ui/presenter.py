"""Projeções textuais compartilhadas pelos dois adaptadores de terminal."""

import textwrap

from castle_invasion.systems.game import Game
from castle_invasion.systems.movement import DIRECTIONS, get_new_position

HELP = [
    "EXPLORAÇÃO: n / s / l / o (norte, sul, leste, oeste)",
    "inspecionar — procura e coleta objetos uma única vez por sala",
    "abrir — tenta abrir o baú do objetivo",
    "COMBATE: atacar (a), defender (d), curar (c), pocao (p), fugir",
    "equipar N — ativa o slot 1, 2 ou 3 (consome turno em combate)",
    "pocao [id] — usa um consumível; sem ID usa o primeiro disponível",
    "pegar N [slot] — coleta objeto do chão; troca arma se informar slot",
    "pegar N trocar — substitui a cura equipada; a antiga fica no chão",
    "CONSULTAS: olhar, mapa (m), inventario (i), ajuda (?) — sem gastar turno",
    "PARTIDA: salvar, carregar, novo, sair (q)",
    "Salvar/carregar usa o arquivo informado por --save. Não há autosave.",
    "Cura percentual usa a vida máxima; cooldown conta ações válidas posteriores.",
    "Fugir recebe um ataque e volta à sala anterior. O inimigo conserva o HP.",
]


def wrap_lines(lines: list[str], width: int) -> list[str]:
    result = []
    for line in lines:
        result.extend(textwrap.wrap(line, width=max(20, width), replace_whitespace=False) or [""])
    return result


def status_lines(game: Game, width=88, art=True) -> list[str]:
    state, data = game.state, game.content
    player = state.player
    inv = player.inventory
    weapon = data["weapons"].get(inv.equipped_weapon, {"name": "Punhos"})
    lines = [
        f"{data['title']} | {game.current_room}",
        f"{player.name} | HP {player.health:g}/{player.max_health:g} | Nível {player.level} | XP {player.xp}",
        f"Arma: {weapon['name']} (slot {inv.active_slot + 1})",
        "",
    ]
    if state.won:
        lines += ["VITÓRIA", data["objective"]["message"], "novo / carregar / sair"]
    elif not player.alive:
        lines += ["DERROTA — carregar / novo / sair"]
    elif state.battle:
        enemy = state.enemies[state.battle.enemy_id]
        definition = data["enemies"][enemy.id]
        if art:
            enemy_art = data["sprites"]["enemies"][definition["sprite_key"]]
            player_art = data["sprites"]["player"]
            left_width = max(map(len, player_art), default=0) + 4
            if width >= left_width + max(map(len, enemy_art), default=0):
                lines += [
                    (player_art[i] if i < len(player_art) else "").ljust(left_width)
                    + (enemy_art[i] if i < len(enemy_art) else "")
                    for i in range(max(len(player_art), len(enemy_art)))
                ]
            else:
                lines += [line[:width] for line in enemy_art]
        lines += [
            f"{definition['name']} | HP {enemy.health:g}/{definition['health']:g}",
            f"Cura: {data['heals'][inv.heal]['name'] if inv.heal else 'nenhuma'} | Cooldown: {state.battle.cooldown}",
            "atacar / defender / curar / pocao / equipar N / fugir",
        ]
    else:
        lines += data["rooms"][game.current_room]["description"]
        exits = [
            direction
            for direction in DIRECTIONS
            if get_new_position(player.position, direction, data["map"]) != player.position
        ]
        lines += ["", "Saídas: " + ", ".join(exits), "inspecionar / inventario / mapa / abrir"]
        for i, entry in enumerate(state.rooms[game.current_room].ground, 1):
            lines.append(f"Chão {i}: {data.loot_name(entry.kind, entry.id)} ({entry.kind})")
    return wrap_lines(lines, width)


def inventory_lines(game: Game) -> list[str]:
    inv, data = game.state.player.inventory, game.content
    lines = ["INVENTÁRIO"]
    for i, weapon in enumerate(inv.weapons):
        name = data["weapons"][weapon]["name"] if weapon else "vazio"
        marker = " [ATIVA]" if i == inv.active_slot else ""
        damage = f" — dano {data['weapons'][weapon]['damage']:g}" if weapon else ""
        lines.append(f"Slot {i + 1}: {name}{damage}{marker}")
    lines.append("Cura: " + (data["heals"][inv.heal]["name"] if inv.heal else "nenhuma"))
    lines += [f"{data['items'][key]['name']} x{count} ({key})" for key, count in inv.items.items()]
    return lines


def map_lines(game: Game) -> list[str]:
    lines = [
        "MAPA — cada linha abaixo corresponde a uma linha do castelo.",
        "@ atual | + visitada | ? não visitada | -- sem sala",
    ]
    for r, row in enumerate(game.content["map"], 1):
        lines.append(f"Linha {r}:")
        for c, room in enumerate(row, 1):
            marker = "@" if room == game.current_room else "+" if room in game.state.visited else "?"
            lines.append(f"  {c}. {marker} {room}" if room else f"  {c}. --")
    return lines
