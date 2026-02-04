from core.item_registry import get_heal, get_weapon
from entities.enemy import Enemy
from entities.player import Player
from systems.inventory_system import get_equipped_weapon

def calculate_player_damage(player: Player):
    weapon_id = get_equipped_weapon(player)
    return get_weapon(weapon_id)['damage'] if weapon_id else 2

def calculate_enemy_damage(enemy: Enemy):
    return enemy.damage

def player_attack_enemy(player: Player, enemy: Enemy):
    dmg = calculate_player_damage(player)
    enemy.take_damage(dmg)
    return dmg

def enemy_attack_player(enemy: Enemy, player: Player, modifier: float):
    dmg = enemy.got_defended(modifier)
    player.take_damage(dmg)

def use_heal(player: Player, heal_id):
    heal = get_heal(heal_id)
    player.heal(heal["heal_multiplier"])
    return heal

def enemy_is_dead(enemy: Enemy):
    return enemy.health <= 0

def player_is_dead(player: Player):
    return player.health <= 0




