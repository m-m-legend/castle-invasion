from core.item_registry import get_heal, get_weapon
from entities.enemy import Enemy
from entities.player import Player
from systems.inventory_system import equip_weapon, get_equipped_heal, get_equipped_weapon
class BattleController:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.cooldown = 0
        self.modifier = 1.0
        self.messages = []
        self.loot_events = []
    
    def calculate_player_damage(self):
        weapon_id = get_equipped_weapon(self.player)
        return get_weapon(weapon_id)['damage'] if weapon_id else 2

    def player_attack(self):
        dmg = self.calculate_player_damage()
        self.enemy.take_damage(dmg)
        self.messages.append(f"Você causou {dmg} de dano.")

    def player_defend(self):
        weapon_id = get_equipped_weapon(self.player)
        if not weapon_id:
            self.messages.append("Nenhuma arma equipada!")
            return
        weapon = get_weapon(weapon_id)
        if not weapon.get("block"):
            self.messages.append("Arma equipada não pode defender!")
            return
        self.modifier = weapon["block"]
        self.messages.append(f"Você se defendeu em {self.modifier}%.")

    def player_use_heal(self):
        heal_id = get_equipped_heal(self.player)
        if not heal_id:
            self.messages.append("Nenhuma cura equipada!")
            return 
        if self.cooldown <= 0:
            heal = get_heal(heal_id)
            self.player.heal(heal["heal_multiplier"])
            self.cooldown = heal["cooldown"]
            self.modifier = heal["enemy_damage_multiplier"]
            if heal.get("message"):
                self.messages.append(heal["message"])
            self.messages.append(
    f"Você foi curado em {(heal['heal_multiplier'] - 1) * 100:.0f}%"
)
        else:
            self.messages.append(f"Espere o cooldown de {self.cooldown} turno(s)")
    
    def player_change_weapon(self, slot: int):
        if slot not in (1, 2, 3):
            self.messages.append("Entrada inválida.")
            return
        weapon_id = equip_weapon(self.player, slot)
        if not weapon_id:
            self.messages.append("Nenhuma arma nesse slot.")
            return
        weapon = get_weapon(weapon_id)
        self.messages.append(
            f"Arma '{weapon['name']}' equipada do slot {slot}."
        )
        
    def player_is_dead(self):
        return self.player.health <= 0

    def enemy_turn(self):
        dmg = self.enemy.got_defended(self.modifier)
        self.player.take_damage(dmg)
        self.modifier = 1.0
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def resolve_loot(self):
        loot = self.enemy.loot
        if not loot:
            return

        if loot.get("weapons"):
            for weapon_id in loot["weapons"]:
                self.loot_events.append({
                    "type": "weapon",
                    "id": weapon_id
                })

        if loot.get("items"):
            for item_id in loot["items"]:
                self.loot_events.append({
                    "type": "item",
                    "id": item_id
                })
        
        if loot.get("heals"):
            for heal_id in loot["heals"]:
                self.loot_events.append({
                    "type": "heal",
                    "id": heal_id
                })

    def consume_loot(self):
        loot = self.loot_events.copy()
        self.loot_events.clear()
        return loot

    def consume_messages(self):
        messages = self.messages.copy()
        self.messages.clear()
        return messages
            
    def enemy_is_dead(self):
        if self.enemy.health <= 0:
            if not self.loot_events:
                self.resolve_loot()
            return True
        return False




