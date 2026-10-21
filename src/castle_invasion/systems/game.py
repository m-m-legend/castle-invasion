"""Casos de uso da partida. A mesma API atende terminal, testes e futuras UIs."""

from castle_invasion.core.content import Content
from castle_invasion.entities.models import BattleState, Enemy, GameState, Loot, Player, RoomState
from castle_invasion.systems.combat_system import BattleController, use_consumable
from castle_invasion.systems.movement import DIRECTIONS, get_new_position


class Game:
    def __init__(self, content: Content, state: GameState):
        self.content = content
        self.state = state

    @classmethod
    def new(cls, content: Content, name: str = "Aventureiro") -> "Game":
        settings = content["player"]
        player = Player(
            name.strip()[:40] or "Aventureiro",
            settings["max_health"],
            settings["max_health"],
            content.position_of(settings["start_room"]),
        )
        for slot, weapon in enumerate(settings["weapons"]):
            player.inventory.weapons[slot] = weapon
        player.inventory.heal = settings["heal"]
        for item in settings["items"]:
            player.inventory.add_item(item)
        state = GameState(
            player,
            {room: RoomState() for room in content["rooms"]},
            {key: Enemy(key, data["health"]) for key, data in content["enemies"].items()},
        )
        game = cls(content, state)
        game._enter_room()
        return game

    @property
    def current_room(self) -> str:
        return self.content.room_at(self.state.player.position)

    def _enter_room(self) -> list[str]:
        self.state.visited.add(self.current_room)
        for key, enemy in self.state.enemies.items():
            if enemy.alive and self.content["enemies"][key]["placement"] == self.current_room:
                self.state.battle = BattleState(key)
                return [f"{self.content['enemies'][key]['name']} bloqueia seu caminho!"]
        self.state.battle = None
        return []

    def command(self, raw: str) -> list[str]:
        tokens = raw.strip().lower().split()
        if not tokens:
            return []
        action = tokens[0]
        args = tokens[1:]
        aliases = {
            "n": "norte",
            "s": "sul",
            "l": "leste",
            "o": "oeste",
            "a": "atacar",
            "d": "defender",
            "c": "curar",
            "p": "pocao",
            "poção": "pocao",
            "poção_cura": "pocao",
        }
        action = aliases.get(action, action)
        if self.state.won:
            return ["A campanha terminou em vitória. Use novo para recomeçar."]
        if not self.state.player.alive:
            return ["Você foi derrotado. Carregue uma partida ou use novo."]
        if len(args) > (2 if action == "pegar" else 1 if action in ("equipar", "pocao") else 0):
            return ["Argumentos inválidos. Consulte ajuda."]

        if self.state.battle:
            if action == "fugir":
                return self.flee()
            battle = self.state.battle
            enemy = self.state.enemies[battle.enemy_id]
            _, messages = BattleController(self.state.player, enemy, battle, self.content).take_turn(
                action, args[0] if args else ""
            )
            if not enemy.alive:
                messages.extend(self._resolve_victory(enemy))
            elif not self.state.player.alive:
                messages.append("Você caiu em combate. Fim de jogo.")
            return messages

        if action in DIRECTIONS:
            return self.move(action)
        if action == "inspecionar":
            return self.inspect()
        if action == "pegar":
            return self.pick_up(args)
        if action == "equipar":
            if len(args) == 1 and args[0].isdigit() and self.state.player.inventory.equip(int(args[0])):
                return ["Arma equipada."]
            return ["Escolha um slot ocupado: equipar 1, 2 ou 3."]
        if action == "pocao":
            return use_consumable(self.state.player, self.content, args[0] if args else "")[1]
        if action == "abrir":
            objective = self.content["objective"]
            if self.current_room != objective["room"]:
                return [f"O objetivo está em {objective['room']}."]
            if not self.state.player.inventory.items.get(objective["key"]):
                name = self.content["items"][objective["key"]]["name"]
                return [f"O baú está trancado. Você precisa de {name}."]
            self.state.won = True
            return [objective["message"]]
        return ["Comando indisponível. Digite ajuda para ver as opções."]

    def move(self, direction: str) -> list[str]:
        player = self.state.player
        new_position = get_new_position(player.position, direction, self.content["map"])
        if new_position == player.position:
            return ["Não há passagem nessa direção."]
        player.last_position, player.position = player.position, new_position
        return [f"Você entrou em {self.current_room}."] + self._enter_room()

    def inspect(self) -> list[str]:
        room = self.state.rooms[self.current_room]
        if room.inspected:
            return ["Você já inspecionou esta sala. Os objetos restantes continuam no chão."]
        room.inspected = True
        room.ground.extend(Loot(**entry) for entry in self.content["rooms"][self.current_room]["loot"])
        return ["Sala inspecionada."] + self._collect_available()

    def _collect_available(self) -> list[str]:
        """Objetos que não cabem ficam no chão; nunca são descartados silenciosamente."""
        room = self.state.rooms[self.current_room]
        messages = []
        for entry in list(room.ground):
            inventory = self.state.player.inventory
            if entry.kind == "item":
                inventory.add_item(entry.id)
            elif entry.kind == "weapon" and None in inventory.weapons:
                inventory.weapons[inventory.weapons.index(None)] = entry.id
            elif entry.kind == "heal" and inventory.heal is None:
                inventory.heal = entry.id
            else:
                continue
            room.ground.remove(entry)
            messages.append(f"Recebeu: {self.content.loot_name(entry.kind, entry.id)}.")
        if room.ground:
            messages.append("Há objetos no chão. Use pegar N SLOT ou pegar N trocar (cura).")
        return messages or ["Nada para coletar."]

    def pick_up(self, args: list[str]) -> list[str]:
        ground = self.state.rooms[self.current_room].ground
        if not args or not args[0].isdigit() or not 1 <= int(args[0]) <= len(ground):
            return ["Use pegar N, com o número de um objeto no chão."]
        entry = ground[int(args[0]) - 1]
        inventory = self.state.player.inventory
        replaced = None
        if entry.kind == "weapon":
            if len(args) == 2:
                if args[1] not in ("1", "2", "3"):
                    return ["O slot deve ser 1, 2 ou 3."]
                slot = int(args[1]) - 1
            elif None in inventory.weapons:
                slot = inventory.weapons.index(None)
            else:
                return ["Slots cheios. Use pegar N SLOT para trocar e deixar a arma antiga no chão."]
            replaced = inventory.weapons[slot]
            inventory.weapons[slot] = entry.id
        elif entry.kind == "heal":
            if inventory.heal and (len(args) != 2 or args[1] != "trocar"):
                return ["Use pegar N trocar para substituir a cura; a antiga fica no chão."]
            replaced, inventory.heal = inventory.heal, entry.id
        else:
            inventory.add_item(entry.id)
        ground.remove(entry)
        if replaced:
            ground.append(Loot(entry.kind, replaced))
        return [f"Coletou {self.content.loot_name(entry.kind, entry.id)}."]

    def _resolve_victory(self, enemy: Enemy) -> list[str]:
        data = self.content["enemies"][enemy.id]
        messages = [f"Você derrotou {data['name']}!"]
        if not enemy.rewarded:
            enemy.rewarded = True
            self.state.rooms[self.current_room].ground.extend(Loot(**entry) for entry in data["loot"])
            player = self.state.player
            player.xp += data["xp"]
            rules = self.content["rules"]
            new_level = 1 + player.xp // rules["xp_per_level"]
            levels = new_level - player.level
            if levels > 0:
                player.level = new_level
                player.max_health += levels * rules["health_per_level"]
                player.heal(levels * rules["health_per_level"])
                messages.append(f"Subiu para o nível {new_level}!")
            messages.extend(self._collect_available())
        messages.extend(self._enter_room())
        return messages

    def flee(self) -> list[str]:
        player = self.state.player
        if player.last_position is None:
            return ["Não há sala anterior para fugir."]
        enemy_id = self.state.battle.enemy_id
        damage = self.content["enemies"][enemy_id]["damage"] * self.content["rules"]["flee_damage_multiplier"]
        player.take_damage(damage)
        if not player.alive:
            return [f"Você sofreu {damage:g} de dano ao fugir e foi derrotado."]
        player.position, player.last_position = player.last_position, player.position
        return [f"Fugiu para {self.current_room}, sofrendo {damage:g} de dano."] + self._enter_room()
