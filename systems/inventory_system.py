from entities.player import Player

def get_equipped_weapon(player: Player):
    return player.inventory.get_equipped_weapon()

def get_equipped_heal(player: Player):
    return player.inventory.get_heal()

def equip_weapon(player: Player, slot: int):
    return player.inventory.equip_weapon(slot)

def add_item_system(player: Player, new_item: str):
    player.inventory.add_item(new_item)

def has_heal(player: Player):
    return player.inventory.are_there_heals()

def get_inventory_summary(player: Player):
    return player.inventory.get_inventory_summary()

def add_weapon_auto(player: Player, new_weapon: str):
    return player.inventory.add_weapon_auto(new_weapon)

def substitute_weapon(player: Player, slot: int, new_weapon: str):
    return player.inventory.substitute_weapon(slot, new_weapon)

def set_heal(player: Player, new_heal: str):
    player.inventory.set_heal(new_heal)

def substitute_heal(player: Player, new_heal):
    return player.inventory.substitute_heal(new_heal)