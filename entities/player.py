from systems.movement import get_new_position
from entities.inventory import Inventory

class Player:
    def __init__(self, name: str, inventory: Inventory, health: float, max_health=100, position=None):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.position = position or (0,0)
        self.inventory = inventory
        self.last_position = None
    def move(self, direction, game_map):
        new_pos = get_new_position(self.position, direction, game_map)
        if new_pos != self.position:
            self.last_position = self.position
            self.position = new_pos
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
    def is_alive(self):
        return self.health > 0
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"Player {self.name} - Health: {self.health}, Position: {self.position}"