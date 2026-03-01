from data.enemies_data import ENEMIES
from entities.player import Player
from entities.enemy import Enemy
from systems.map_system import get_room_name

class GameState:
    def __init__(self, player: Player, game_map: list[list]):
        self.player = player
        self.running = True
        self.in_battle = False
        self.rooms = {} # Tracks everything about the rooms and the items (e.g., inspected, unlocked, checked [...])
        self.game_map = game_map
        self.current_room = get_room_name(player.position, self.game_map)
        self.spawn_enemies()
    def is_running(self):
        return self.running 
    def is_in_battle(self):
        return self.in_battle
    def close(self):
        self.running = False
    def start_battle(self):
        self.in_battle = True
    def end_battle(self):
        self.in_battle = False
    def ensure_room(self, room_name):
        return self.rooms.setdefault(room_name, {
            "unlocked": False,
            "inspected": False,
            "items": {},
            "enemies": {} # enemy_id -> runtime state
        })
    def unlock_room(self, room_name: str):
        self.ensure_room(room_name)['unlocked'] = True
    def inspect_room(self, room_name: str):
        self.ensure_room(room_name)['inspected'] = True
    def register_item(self, room, item):
        self.ensure_room(room)["items"][item] = {"checked": False}
    def check_item(self, room, item):
        self.ensure_room(room)["items"][item]["checked"] = True
    def is_item_checked(self, room, item):
        return self.rooms.get(room, {}).get("items", {}).get(item, {}).get("checked", False)
    def has_item(self, room, item):
        return item in self.rooms.get(room, {}).get("items", {})
    def update_room(self):
        self.current_room = get_room_name(self.player.position, self.game_map)
    def move_player(self, direction):
        self.player.move(direction, self.game_map)
        self.update_room()
    def spawn_enemies(self):
        for enemy_id, data in ENEMIES.items():
            enemy = Enemy(
                id=enemy_id,
                name=data["name"],
                health=data["health"],
                damage=data["damage"],
                sprite_key=data["sprite_key"],
                placement=data["placement"],
                loot = data["loot"]
            )
            room = data["placement"]
            self.register_enemy(room, enemy_id, enemy)
    def register_enemy(self, room, enemy_id, enemy_obj):
        self.ensure_room(room)["enemies"][enemy_id] = {
            "entity": enemy_obj,
            "defeated": False
        }
    def defeat_enemy(self, room, enemy_id):
        self.ensure_room(room)["enemies"][enemy_id]["defeated"] = True
    def is_enemy_alive(self, room, enemy_id):
        return not self.rooms.get(room, {}).get("enemies", {}).get(enemy_id, {}).get("defeated", True)
    def get_alive_enemies(self, room):
        enemies = self.rooms.get(room, {}).get("enemies", {})
        return [e["entity"] for e in enemies.values() if not e["defeated"]]
    def has_enemies(self, room):
        return any(not e["defeated"] for e in self.rooms.get(room, {}).get("enemies", {}).values())




